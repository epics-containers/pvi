# Taken from detail_converter
# /dls_sw/prod/common/python/RHEL7-x86_64/dls_guibuilder/1-3-1/dls_guibuilder/detailConverter.py
import re
from pathlib import Path


class CSSitem:
    """General class for CSS items, with name and location"""

    def __init__(self, Name, x, y):
        self.Name = Name
        self.x = x
        self.y = y


class Section(CSSitem):
    """Specific section object for groups of PVs"""

    def __init__(self, Name, x, y, xmax, ymax, fileNo):
        """Initialise object with name, x and y range,
        file number and empty list of PVs"""
        CSSitem.__init__(self, Name, x, y)
        self.xmax = xmax
        self.ymax = ymax
        self.fileNo = fileNo
        self.PVs = []

    def __str__(self):
        """General description of the section"""
        return (
            self.Name
            + " is from "
            + str(self.x)
            + ", "
            + str(self.y)
            + " to "
            + str(self.xmax)
            + ", "
            + str(self.ymax)
        )

    def inSection(self, x_in, y_in, fileNo_in):
        """Check whether an object (usually PV) is in
        the section based on location and file number"""
        if (
            (self.x <= x_in <= self.xmax)
            and (self.y <= y_in <= self.ymax)
            and (fileNo_in == self.fileNo)
        ):
            return True
        else:
            return False

    def addPV(self, Name_PV, x_PV, y_PV, Type_PV):
        """Add a PV to the list of PVs in the section object"""
        self.PVs.append(PV(Name_PV, x_PV, y_PV, Type_PV))


class PV(CSSitem):
    """Specific PV object which stores the type of widget"""

    def __init__(self, Name, x, y, Type):
        """Initialise the PV object with name, location and type"""
        CSSitem.__init__(self, Name, x, y)
        self.Type = Type


def pv_group(edl: Path):
    """Group the edl pvs based on the boxes they are in"""

    # Get information from edl_files
    edl_file = edl
    fileNo = 1  # todo: change so it doesn't need file number

    # Initialise blank section list
    sectionList = []
    # For PVs which cannot be associated with a section
    lostPVs = []

    # Open and read edl file as one big string
    f = open(edl_file, "r")
    readFile = f.read()

    # Use regex to search for section names - "  Section Name  " in edl files
    sectionHeaderSearch = re.findall(r'"  (.*?)  "', readFile)

    # Split document up into lines
    readFileLines = readFile.splitlines()

    xheader = []
    yheader = []

    # Find line number of section header
    for i in range(len(sectionHeaderSearch)):
        # sub = sectionHeaderSearch[i]
        # result = next((i for i, s in enumerate(readFileLines) if sub in s), None)
        for j in range(len(readFileLines)):
            if '"  ' + sectionHeaderSearch[i] + '  "' in readFileLines[j]:
                # print(j)
                j = j - 1
                # Spaces added to pattern to avoid matching x or y
                # in other attributes or labels
                while (re.search("y ", readFileLines[j])) is None:
                    j = j - 1
                yheader.append((int(readFileLines[j][2:])))
                while (re.search("x ", readFileLines[j])) is None:
                    j = j - 1
                xheader.append((int(readFileLines[j][2:])))
                break

    # Find out where the rectangles are - activeRectangleClass
    for j in range(len(readFileLines)):
        if re.search(r"activeRectangleClass", readFileLines[j]):
            # xrectangle = int(readFileLines[i + 5][2:])
            # yrectangle = int(readFileLines[i + 6][2:])
            # xrectangleWidth = int(readFileLines[i + 7][2:])
            # yrectangleHeight = int(readFileLines[i + 8][2:])
            j = j + 1
            while (re.search("x ", readFileLines[j])) is None:
                j = j + 1
            xrectangle = int(readFileLines[j][2:])
            while (re.search("y ", readFileLines[j])) is None:
                j = j + 1
            yrectangle = int(readFileLines[j][2:])
            while (re.search("w ", readFileLines[j])) is None:
                j = j + 1
            xrectangleWidth = int(readFileLines[j][2:])
            while (re.search("h ", readFileLines[j])) is None:
                j = j + 1
            yrectangleHeight = int(readFileLines[j][2:])

            # Associate the rectangle with a section header
            # and create a new section object
            for j in range(len(sectionHeaderSearch)):
                if xrectangle > 0:
                    if (
                        xrectangle <= xheader[j] <= (xrectangle + xrectangleWidth)
                    ) and (
                        yrectangle <= yheader[j] + 10 <= (yrectangle + yrectangleHeight)
                    ):
                        sectionList.append(
                            Section(
                                sectionHeaderSearch[j],
                                xrectangle,
                                yrectangle,
                                (xrectangle + xrectangleWidth),
                                (yrectangle + yrectangleHeight),
                                fileNo,
                            )
                        )

    # Next section of code: Find PVs and allocate them to the relevant section
    """
    Psuedocode:
        find PVname, PVx and PVy
        for Section in sectionList
            if Section.inSection(PVx, PVy)
                Section.addPV(PVname, PVx, PVy, PVtype)
        add to lostPVs list if not found in sections
    """

    # Regex expression with many escapes to find controlPVs and some visPVs
    pvSearch = re.findall(r'controlPv "(.*?)"', readFile)
    pvSearch = pvSearch + re.findall(r'visPv "(.*?)(?<!.DISA)"', readFile)

    # Remove macros from PV names
    # for i in range(len(pvSearch)):
    #    pvSearch[i] = re.sub(r'\$\((.*)\)', '', pvSearch[i])

    # Get location and type of PV
    # j and z interaction guarantees one pass of file for each pv,
    # hopefully avoiding repeats or getting stuck
    # in weird places
    j = 0
    for i in range(len(pvSearch)):
        for z in range(len(readFileLines)):
            # Searches for controlPv and visPv
            # Stores macros in PV.name
            if (
                re.match(
                    r'controlPv(.*)"(' + re.escape(pvSearch[i]) + r')"',
                    readFileLines[j],
                )
            ) or (
                re.match(
                    r'visPv(.*)"(' + re.escape(pvSearch[i]) + r')"',
                    readFileLines[j],
                )
            ):
                # Crawl up to find attributes
                PVname = pvSearch[i]
                # Pre emptively avoid looking in same line as n
                j = j - 1
                # Spaces added to pattern to avoid matching x or y
                # in other attributes or labels
                while (re.search("y ", readFileLines[j])) is None:
                    j = j - 1
                PVy = int(readFileLines[j][2:])
                while (re.search("x ", readFileLines[j])) is None:
                    j = j - 1
                PVx = int(readFileLines[j][2:])
                while re.search("object ", readFileLines[j]) is None:
                    j = j - 1
                PVtype = readFileLines[j][7:]
                # Remove any punctuation from object name
                # (Do not append this line in your edl file!!)
                PVtype = re.sub(r"[^\w\s](.*)", "", PVtype)

                # Go to end of widget description
                while readFileLines[j] != "":
                    j = j + 1
                # Check for activeXTextDspClass which are readbacks
                # - require different handling than demands
                if (PVtype == "activeXTextDspClass") and (re.search("_RBV", PVname)):
                    PVtype = "activeXTextDspClassRBV"

                if PVtype == "activeSliderClass":
                    pass

                # Put in relevant section
                foundPV = 0
                for (
                    s
                ) in (
                    sectionList
                ):  # Small s used to differentiate iterator from class name
                    if s.inSection(PVx, PVy, fileNo):
                        s.addPV(PVname, PVx, PVy, PVtype)
                        foundPV = 1
                        break
                if foundPV == 0:
                    # Add to lost PVs if not found
                    lostPVs.append(PV(PVname, PVx, PVy, PVtype))
                break
            j = j + 1
            # wrap
            if j == len(readFileLines):
                j = 0

    # Sort PVs in each section based on y then x
    for s in sectionList:
        s.PVs.sort(key=lambda x: (x.y, x.x), reverse=False)
    # Sort lost PVs (this will not result in a clean conversion if
    # there are lost PVs across different files
    lostPVs.sort(key=lambda x: (x.y, x.x), reverse=False)

    # Sort sectionList based on fileNo, then ymin, then xmin
    sectionList.sort(key=lambda x: (x.fileNo, x.y, x.x), reverse=False)

    sectionDict = {}
    for section in sectionList:
        # no longer need the pv object, just the name
        pvs = []
        for i in range(len(section.PVs)):
            pv = section.PVs[i]
            pv_extractor = re.compile(r"\$\(P\)\$\(R\)([a-zA-Z]+)")
            name = re.findall(pv_extractor, pv.Name)
            pvs.append(name[0])

        sectionDict[section.Name] = pvs

    return sectionDict
