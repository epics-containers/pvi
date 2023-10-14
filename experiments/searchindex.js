Search.setIndex({"docnames": ["developer/explanations/decisions", "developer/explanations/decisions/0001-record-architecture-decisions", "developer/explanations/decisions/0002-switched-to-pip-skeleton", "developer/explanations/original-design", "developer/how-to/build-docs", "developer/how-to/contribute", "developer/how-to/lint", "developer/how-to/make-release", "developer/how-to/pin-requirements", "developer/how-to/run-tests", "developer/how-to/static-analysis", "developer/how-to/test-container", "developer/how-to/update-tools", "developer/how-to/write-a-formatter", "developer/index", "developer/reference/standards", "developer/tutorials/dev-install", "genindex", "index", "user/explanations/docs-structure", "user/how-to/run-container", "user/index", "user/reference/api", "user/tutorials/installation"], "filenames": ["developer/explanations/decisions.rst", "developer/explanations/decisions/0001-record-architecture-decisions.rst", "developer/explanations/decisions/0002-switched-to-pip-skeleton.rst", "developer/explanations/original-design.rst", "developer/how-to/build-docs.rst", "developer/how-to/contribute.rst", "developer/how-to/lint.rst", "developer/how-to/make-release.rst", "developer/how-to/pin-requirements.rst", "developer/how-to/run-tests.rst", "developer/how-to/static-analysis.rst", "developer/how-to/test-container.rst", "developer/how-to/update-tools.rst", "developer/how-to/write-a-formatter.rst", "developer/index.rst", "developer/reference/standards.rst", "developer/tutorials/dev-install.rst", "genindex.rst", "index.rst", "user/explanations/docs-structure.rst", "user/how-to/run-container.rst", "user/index.rst", "user/reference/api.rst", "user/tutorials/installation.rst"], "titles": ["Architectural Decision Records", "1. Record architecture decisions", "2. Adopt python3-pip-skeleton for project structure", "Original Design", "Build the docs using sphinx", "Contributing to the project", "Run linting using pre-commit", "Make a release", "Pinning Requirements", "Run the tests using pytest", "Run static analysis using mypy", "Container Local Build and Test", "Update the tools", "How to Write a Site Specific Formatter", "Developer Guide", "Standards", "Developer install", "API Index", "PVI", "About the documentation", "Run in a container", "User Guide", "API", "Installation"], "terms": {"we": [0, 1, 2, 3, 5, 8, 13], "major": 0, "adr": [0, 1], "describ": [0, 1, 3, 13], "michael": [0, 1], "nygard": [0, 1], "below": [0, 13], "i": [0, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 19, 21, 22, 23], "list": [0, 8, 13], "our": [0, 13], "current": [0, 3, 12, 13, 18, 23], "1": [0, 3, 13, 15], "2": [0, 3, 13, 15, 18], "adopt": [0, 3], "python3": [0, 8, 12, 16, 23], "pip": [0, 8, 12, 16, 18, 23], "skeleton": [0, 8, 12], "project": [0, 1, 4, 8, 9, 11, 12, 14], "structur": [0, 3, 12], "date": [1, 2, 18], "2022": [1, 2], "02": [1, 2], "18": [1, 2, 3, 13], "accept": [1, 2], "need": [1, 3, 8, 13, 19, 23], "made": [1, 3, 8, 13], "thi": [1, 2, 3, 4, 6, 7, 8, 11, 12, 13, 15, 16, 18, 19, 22, 23], "us": [1, 2, 3, 8, 13, 14, 15, 16, 18, 20, 23], "see": [1, 3, 4, 7], "": [1, 3], "articl": 1, "link": [1, 14, 21], "abov": [1, 3, 6, 13], "To": [1, 7, 8, 11, 12, 13, 16, 20], "creat": [1, 3, 7, 8], "new": [1, 3, 5, 7, 16, 21], "copi": [1, 3, 8], "past": [1, 3], "from": [1, 2, 3, 4, 6, 13, 14, 15, 20, 21, 23], "exist": [1, 3, 5, 23], "ones": 1, "should": [2, 3, 5, 8, 13, 23], "follow": [2, 3, 5, 7, 11, 13, 15, 16], "The": [2, 3, 4, 5, 6, 8, 11, 13, 15, 18, 19, 23], "ensur": [2, 3], "consist": [2, 3], "develop": [2, 11, 18], "environ": [2, 5, 8, 16], "packag": [2, 8, 16], "manag": [2, 3], "have": [2, 3, 5, 6, 8, 11, 13, 16], "switch": 2, "modul": [2, 3, 12, 18], "fix": [2, 8, 11], "set": [2, 3, 5, 6, 8, 13, 15], "tool": [2, 14, 15], "can": [2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 16, 23], "pull": [2, 4, 5, 12, 20], "updat": [2, 3, 8, 14], "latest": [2, 8, 12], "techniqu": [2, 12], "As": [2, 13, 15], "mai": [2, 3, 8], "chang": [2, 4, 5, 6, 8, 12, 18], "could": [2, 3, 18], "differ": [2, 3, 8, 13, 19], "lint": [2, 14, 15, 16], "format": [2, 3, 13, 15], "venv": [2, 16, 23], "setup": [2, 12, 16], "ci": [2, 11], "cd": [2, 11, 16], "page": [3, 4, 7, 8, 15], "wa": 3, "initi": [3, 18], "plan": 3, "what": [3, 5, 13], "would": [3, 11], "do": [3, 6, 8, 10, 11], "produc": 3, "featur": [3, 23], "now": [3, 6, 13, 16, 23], "been": [3, 8, 13, 23], "remov": [3, 13, 18], "onli": [3, 8, 13, 18], "direct": 3, "convers": [3, 13], "devic": [3, 13], "represent": [3, 13], "kept": 3, "record": [3, 14], "case": [3, 13, 16], "full": [3, 8], "integr": [3, 16], "areadetector": 3, "revisit": 3, "futur": [3, 8], "descript": [3, 13, 15], "reduc": [3, 5], "boilerpl": [3, 18], "At": 3, "moment": 3, "you": [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 16, 23], "write": [3, 14, 19], "simpl": 3, "asyn": [3, 18], "port": [3, 18], "code": [3, 4, 6, 16, 18], "lot": 3, "connect": 3, "outsid": 3, "world": 3, "createparam": 3, "section": [3, 18], "lowest": [3, 8], "level": [3, 18], "ar": [3, 4, 5, 8, 13, 15, 18, 19, 20], "all": [3, 5, 6, 8, 11, 13, 18], "quit": [3, 8], "repetit": 3, "each": [3, 6, 8, 13], "layer": 3, "look": [3, 8, 9, 13], "like": [3, 8, 9, 13], "autogener": 3, "much": 3, "extra": 3, "inform": [3, 5, 13, 19], "error": [3, 9], "easi": 3, "via": [3, 11], "name": [3, 13], "lead": 3, "hard": [3, 8], "track": 3, "down": 3, "site": [3, 14], "specif": [3, 14], "style": [3, 13, 15], "ha": [3, 7, 8, 12, 13, 23], "own": [3, 13], "mani": 3, "displai": [3, 13], "rather": [3, 13], "than": [3, 13], "start": [3, 13, 21], "one": [3, 5, 8, 13, 19], "convert": [3, 13], "take": [3, 8, 13, 16], "cut": 3, "channel": 3, "just": [3, 6], "type": [3, 10, 13, 15, 16, 18, 23], "pv": [3, 13, 18], "widget": 3, "let": 3, "accord": 3, "local": [3, 4, 14, 16], "contain": [3, 5, 8, 13, 14, 15, 16, 18, 21, 23], "about": [3, 21], "expos": 3, "valu": [3, 13, 15], "whether": 3, "writeabl": 3, "read": 3, "etc": [3, 13], "pass": [3, 8, 11], "them": [3, 8, 9, 10, 13], "intermedi": 3, "asynparam": 3, "object": 3, "These": [3, 13, 16], "formatt": [3, 6, 14], "tree": [3, 16], "cpp": [3, 18], "disk": 3, "form": 3, "number": [3, 5, 7, 8, 13, 20, 22], "includ": [3, 4, 21], "base": [3, 4, 13, 18], "superclass": 3, "A": [3, 13], "overrid": 3, "know": 3, "compon": [3, 13], "output": [3, 13], "logic": 3, "arrang": 3, "gui": 3, "group": 3, "also": [3, 4, 5, 6, 9, 14, 21, 23], "incorpor": 3, "asynparamet": 3, "here": [3, 8, 13, 21], "might": [3, 5], "detector": 3, "asynproduc": 3, "prefix": [3, 13], "p": [3, 11, 16], "r": 3, "label": [3, 13], "asyn_port": 3, "address": 3, "addr": 3, "timeout": 3, "parent": [3, 13], "addriv": 3, "componentgroupon": 3, "layout": 3, "grid": 3, "children": [3, 13], "asynbinari": 3, "resetpow": 3, "index_nam": 3, "pilatusresetpow": 3, "drv_info": 3, "reset_pow": 3, "access": [3, 14, 21], "w": [3, 13], "record_field": 3, "znam": 3, "done": [3, 9, 10], "onam": 3, "reset": 3, "asynbusi": 3, "thresholdappli": 3, "pilatusthresholdappli": 3, "threshold_appli": 3, "0": [3, 13], "appli": 3, "asynfloat64": 3, "imagefiletmot": 3, "imag": 3, "pilatusimagefiletmot": 3, "image_file_tmot": 3, "20": [3, 13], "prec": 3, "3": [3, 8, 15, 16, 23], "egu": 3, "wavelength": 3, "pilatuswavelength": 3, "54": 3, "4": [3, 13], "angstrom": 3, "energylow": 3, "pilatusenergylow": 3, "energy_low": 3, "ev": 3, "energyhigh": 3, "pilatusenergyhigh": 3, "energy_high": 3, "detdist": 3, "pilatusdetdist": 3, "det_dist": 3, "1000": 3, "mm": 3, "detvoffset": 3, "pilatusdetvoffset": 3, "det_voffset": 3, "beamx": 3, "pilatusbeamx": 3, "beam_x": 3, "pixel": 3, "beami": 3, "pilatusbeami": 3, "beam_i": 3, "flux": 3, "pilatusflux": 3, "ph": 3, "filtertransm": 3, "pilatusfiltertransm": 3, "filter_transm": 3, "startangl": 3, "pilatusstartangl": 3, "start_angl": 3, "deg": 3, "angleincr": 3, "pilatusangleincr": 3, "angle_incr": 3, "det2theta": 3, "pilatusdet2theta": 3, "det_2theta": 3, "polar": 3, "pilatuspolar": 3, "99": 3, "alpha": 3, "pilatusalpha": 3, "kappa": 3, "pilatuskappa": 3, "phi": 3, "pilatusphi": 3, "phiincr": 3, "pilatusphiincr": 3, "phi_incr": 3, "chi": 3, "pilatuschi": 3, "chiincr": 3, "pilatuschiincr": 3, "chi_incr": 3, "omega": 3, "pilatusomega": 3, "omegaincr": 3, "pilatusomegaincr": 3, "omega_incr": 3, "asynstr": 3, "oscillaxi": 3, "pilatusoscillaxi": 3, "oscill_axi": 3, "x": [3, 13], "cw": 3, "asynlong": 3, "numoscil": 3, "pilatusnumoscil": 3, "num_oscil": 3, "asynwaveform": 3, "badpixelfil": 3, "pilatusbadpixelfil": 3, "bad_pixel_fil": 3, "nelm": 3, "256": 3, "ftvl": 3, "char": 3, "flatfieldfil": 3, "pilatusflatfieldfil": 3, "flat_field_fil": 3, "cbftemplatefil": 3, "pilatuscbftemplatefil": 3, "headerstr": 3, "pilatusheaderstr": 3, "68": 3, "arm": 3, "pilatusarm": 3, "read_record_suffix": 3, "scan": 3, "o": 3, "intr": 3, "unarm": 3, "numbadpixel": 3, "bad": 3, "pilatusnumbadpixel": 3, "num_bad_pixel": 3, "flatfieldvalid": 3, "flat": 3, "field": [3, 13], "valid": 3, "pilatusflatfieldvalid": 3, "flat_field_valid": 3, "No": 3, "ye": 3, "asynint32": 3, "pixelcutoff": 3, "pixelcutoff_rbv": 3, "pilatuspixelcutoff": 3, "pixel_cutoff": 3, "count": 3, "temp0": 3, "temp0_rbv": 3, "pilatusthtemp0": 3, "th_temp_0": 3, "c": 3, "temp1": 3, "temp1_rbv": 3, "pilatusthtemp1": 3, "th_temp_1": 3, "temp2": 3, "temp2_rbv": 3, "pilatusthtemp2": 3, "th_temp_2": 3, "humid0": 3, "humid0_rbv": 3, "pilatusthhumid0": 3, "th_humid_0": 3, "humid1": 3, "humid1_rbv": 3, "pilatusthhumid1": 3, "th_humid_1": 3, "humid2": 3, "humid2_rbv": 3, "pilatusthhumid2": 3, "th_humid_2": 3, "tvxversion": 3, "tvxversion_rbv": 3, "pilatustvxvers": 3, "resetpowertim": 3, "power": 3, "wait": 3, "pilatusresetpowertim": 3, "reset_power_tim": 3, "second": 3, "delaytim": 3, "pilatusdelaytim": 3, "delay_tim": 3, "6": 3, "thresholdenergi": 3, "energi": 3, "threshold": 3, "pilatusthreshold": 3, "10": [3, 13], "000": 3, "kev": 3, "thresholdautoappli": 3, "pilatusthresholdautoappli": 3, "threshold_auto_appli": 3, "rai": 3, "pilatusenergi": 3, "minflatfield": 3, "minimum": [3, 8], "pilatusminflatfield": 3, "min_flat_field": 3, "100": [3, 5], "asynmultibitbinari": 3, "gapfil": 3, "pilatusgapfil": 3, "gap_fil": 3, "zrvl": 3, "onvl": 3, "twvl": 3, "zrst": 3, "n": 3, "onst": 3, "twst": 3, "progressbartest": 3, "progressbar": [3, 13], "progress": 3, "read_widget": 3, "50": 3, "instanc": [3, 13], "basic": 3, "combo": 3, "textinput": 3, "textupd": [3, 13], "led": [3, 13], "some": [3, 8], "creation": [3, 19], "hint": [3, 15], "display_form": 3, "y": [3, 13], "width": [3, 13], "height": [3, 13], "colour": 3, "thei": [3, 13, 19], "repres": [3, 13, 19], "either": [3, 16], "singl": [3, 13, 18], "pair": 3, "demand": 3, "readback": 3, "consum": [3, 8], "size": [3, 13], "custom": [3, 13], "mean": [3, 8, 12, 13], "default": [3, 13], "big": [3, 5], "box": 3, "anoth": 3, "make": [3, 4, 5, 13, 14], "littl": 3, "per": 3, "cover": 3, "so": [3, 8, 13, 16, 18, 23], "blue": 3, "grei": 3, "medm": 3, "green": 3, "edm": 3, "fit": [3, 5], "guid": [3, 13, 15, 18, 19], "reproduc": 3, "tabular": 3, "csv": 3, "rst": 3, "doc": [3, 13, 14, 15, 16], "index": [3, 4, 13, 21], "variabl": [3, 13], "interfac": [3, 18, 23], "drvinfo": 3, "string": [3, 13], "bo": 3, "busi": 3, "ao": 3, "asynoctetwrit": 3, "stringout": 3, "longout": 3, "waveform": 3, "bi": 3, "longin": 3, "ai": 3, "asynoctetread": 3, "stringin": 3, "rw": 3, "resetpowertime_rbv": 3, "delaytime_rbv": 3, "thresholdenergy_rbv": 3, "thresholdautoapply_rbv": 3, "energy_rbv": 3, "minflatfield_rbv": 3, "gapfill_rbv": 3, "mbbo": 3, "mbbi": 3, "progressbartest_rbv": 3, "am": 3, "fairli": 3, "happi": 3, "scheme": 3, "out": [3, 8], "implement": 3, "most": [3, 5, 19], "press": 3, "process": [3, 4, 15], "probabl": 3, "If": [3, 4, 5, 6, 11, 23], "cli": [3, 8, 11], "avail": [3, 8, 11, 13, 20], "build": [3, 8, 14, 15], "product": 3, "part": [3, 13], "end": [3, 5], "user": [3, 6, 13, 18], "regener": 3, "instal": [3, 6, 8, 11, 14, 18, 20, 21], "adgenicam": 3, "genicamproduc": 3, "took": 3, "path": [3, 13, 23], "genicam": 3, "xml": [3, 9], "suggest": 3, "adl": [3, 13], "edl": [3, 13], "exampl": [3, 8, 11, 13, 15], "makeadl": 3, "py": [3, 13], "expand": 3, "opi": [3, 18], "bob": [3, 13], "nativ": 3, "avoid": [3, 13], "header": 3, "defin": [3, 8, 15], "In": [3, 8, 11, 13], "pilatusdetectorparamset": 3, "h": [3, 13], "ifndef": 3, "pilatusdetectorparamset_h": 3, "addriverparamset": 3, "pilatusresetpowerstr": 3, "pilatusthresholdapplystr": 3, "pilatusimagefiletmotstr": 3, "pilatuswavelengthstr": 3, "pilatusenergylowstr": 3, "pilatusenergyhighstr": 3, "pilatusdetdiststr": 3, "pilatusdetvoffsetstr": 3, "pilatusbeamxstr": 3, "pilatusbeamystr": 3, "pilatusfluxstr": 3, "pilatusfiltertransmstr": 3, "pilatusstartanglestr": 3, "pilatusangleincrstr": 3, "pilatusdet2thetastr": 3, "pilatuspolarizationstr": 3, "pilatusalphastr": 3, "pilatuskappastr": 3, "pilatusphistr": 3, "pilatusphiincrstr": 3, "pilatuschistr": 3, "pilatuschiincrstr": 3, "pilatusomegastr": 3, "pilatusomegaincrstr": 3, "pilatusoscillaxisstr": 3, "pilatusnumoscillstr": 3, "pilatusbadpixelfilestr": 3, "pilatusflatfieldfilestr": 3, "pilatuscbftemplatefilestr": 3, "pilatusheaderstringstr": 3, "pilatusarmedstr": 3, "pilatusnumbadpixelsstr": 3, "pilatusflatfieldvalidstr": 3, "pilatuspixelcutoffstr": 3, "pilatusthtemp0str": 3, "pilatusthtemp1str": 3, "pilatusthtemp2str": 3, "pilatusthhumid0str": 3, "pilatusthhumid1str": 3, "pilatusthhumid2str": 3, "pilatustvxversionstr": 3, "pilatusresetpowertimestr": 3, "pilatusdelaytimestr": 3, "pilatusthresholdstr": 3, "pilatusthresholdautoapplystr": 3, "pilatusenergystr": 3, "pilatusminflatfieldstr": 3, "pilatusgapfillstr": 3, "progressbarteststr": 3, "const": 3, "std": 3, "pilatusparamtre": 3, "true": [3, 13, 15], "signalw": 3, "waitforplugin": 3, "checkbox": 3, "emptyfreelist": 3, "ndattributesmacro": 3, "textwrit": [3, 13], "line": [3, 11, 15], "ndattributesfil": 3, "signalr": [3, 13], "adcorevers": 3, "adcoreversion_rbv": 3, "textread": [3, 13], "driververs": 3, "driverversion_rbv": 3, "portnam": 3, "portname_rbv": 3, "manufactur": 3, "manufacturer_rbv": 3, "model": [3, 13], "model_rbv": 3, "serialnumb": 3, "serialnumber_rbv": 3, "sdkversion": 3, "sdkversion_rbv": 3, "firmwarevers": 3, "firmwareversion_rbv": 3, "acquirebusycb": 3, "bayerpattern": 3, "bayerpattern_rbv": 3, "arraysizex": 3, "arraysizex_rbv": 3, "arraysizei": 3, "arraysizey_rbv": 3, "arraysizez": 3, "arraysizez_rbv": 3, "arrays": 3, "arraysize_rbv": 3, "codec": 3, "codec_rbv": 3, "compresseds": 3, "compressedsize_rbv": 3, "uniqueid": 3, "uniqueid_rbv": 3, "timestamp": 3, "timestamp_rbv": 3, "epicstssec": 3, "epicstssec_rbv": 3, "epicstsnsec": 3, "epicstsnsec_rbv": 3, "ndattributesstatu": 3, "poolmaxmem": 3, "poolusedmem": 3, "poolallocbuff": 3, "poolfreebuff": 3, "numqueuedarrai": 3, "signalrw": 3, "acquir": 3, "read_pv": 3, "null": 3, "ndimens": 3, "ndimensions_rbv": 3, "dimens": 3, "dimensions_rbv": 3, "datatyp": 3, "combobox": [3, 13], "choic": 3, "datatype_rbv": 3, "colormod": 3, "colormode_rbv": 3, "arraycount": 3, "arraycounter_rbv": 3, "arraycallback": 3, "arraycallbacks_rbv": 3, "filepathexist": 3, "filepathexists_rbv": 3, "fullfilenam": 3, "fullfilename_rbv": 3, "numcaptur": 3, "numcaptured_rbv": 3, "writestatu": 3, "writemessag": 3, "filepath": 3, "filepath_rbv": 3, "createdirectori": 3, "createdirectory_rbv": 3, "filenam": [3, 13], "filename_rbv": 3, "filenumb": 3, "autoincr": 3, "autoincrement_rbv": 3, "filetempl": 3, "filetemplate_rbv": 3, "autosav": 3, "autosave_rbv": 3, "writefil": 3, "writefile_rbv": 3, "readfil": 3, "readfile_rbv": 3, "fileformat": 3, "fileformat_rbv": 3, "filewritemod": 3, "filewritemode_rbv": 3, "captur": 3, "capture_rbv": 3, "numcapture_rbv": 3, "deletedriverfil": 3, "deletedriverfile_rbv": 3, "lazyopen": 3, "lazyopen_rbv": 3, "tempsuffix": 3, "tempsuffix_rbv": 3, "readstatu": 3, "maxsizex": 3, "maxsizex_rbv": 3, "maxsizei": 3, "maxsizey_rbv": 3, "timeremain": 3, "timeremaining_rbv": 3, "numexposurescount": 3, "numexposurescounter_rbv": 3, "numimagescount": 3, "numimagescounter_rbv": 3, "detectorst": 3, "detectorstate_rbv": 3, "statusmessag": 3, "statusmessage_rbv": 3, "stringtoserv": 3, "stringtoserver_rbv": 3, "stringfromserv": 3, "stringfromserver_rbv": 3, "shutterstatu": 3, "shutterstatus_rbv": 3, "shuttercontrolep": 3, "temperatureactu": 3, "binx": 3, "binx_rbv": 3, "bini": 3, "biny_rbv": 3, "minx": 3, "minx_rbv": 3, "mini": 3, "miny_rbv": 3, "sizex": 3, "sizex_rbv": 3, "sizei": 3, "sizey_rbv": 3, "reversex": 3, "reversex_rbv": 3, "reversei": 3, "reversey_rbv": 3, "acquiretim": 3, "acquiretime_rbv": 3, "acquireperiod": 3, "acquireperiod_rbv": 3, "gain": 3, "gain_rbv": 3, "frametyp": 3, "frametype_rbv": 3, "imagemod": 3, "imagemode_rbv": 3, "triggermod": 3, "triggermode_rbv": 3, "numexposur": 3, "numexposures_rbv": 3, "numimag": 3, "numimages_rbv": 3, "shuttermod": 3, "shuttermode_rbv": 3, "shuttercontrol": 3, "shuttercontrol_rbv": 3, "shutteropendelai": 3, "shutteropendelay_rbv": 3, "shutterclosedelai": 3, "shutterclosedelay_rbv": 3, "temperatur": 3, "temperature_rbv": 3, "public": 3, "virtual": [3, 8], "add": 3, "asynparamint32": 3, "asynparamfloat64": 3, "asynparamoctet": 3, "paramtre": 3, "int": [3, 13, 15], "first_pilatusdetectorparamset_param": 3, "endif": 3, "modifi": 3, "definit": [3, 10], "param": 3, "api": [3, 4, 15, 21], "properti": 3, "automat": [3, 6], "pleas": [3, 5, 7, 15], "edit": [3, 7], "instead": [3, 5, 11, 20], "desc": 3, "dtyp": 3, "pini": 3, "val": 3, "inp": 3, "top": 3, "well": [3, 6], "provid": [3, 8, 12, 13], "thing": [3, 19], "arrayr": 3, "epicsshutt": 3, "final": [3, 13], "element": [3, 13], "multipl": [3, 8, 12, 13], "graphic": 3, "applic": [3, 8, 11], "For": [3, 8, 13, 15], "serv": 3, "low": [3, 18], "overview": 3, "entir": 3, "system": 3, "conveni": 3, "pallett": 3, "construct": 3, "higher": 3, "more": [3, 8, 12, 13, 16, 19, 21], "onc": [3, 8], "an": [3, 4, 6, 8, 12, 13, 18], "after": [3, 8, 13], "script": 3, "newli": 3, "written": [3, 18], "necessari": 3, "delai": 3, "between": [3, 12, 13], "extern": 3, "trigger": 3, "acquisit": 3, "role": [3, 13], "And": [3, 13], "run": [3, 4, 5, 11, 12, 14, 15, 16, 21], "possibli": 3, "It": [3, 6, 8, 9, 10, 13, 18, 23], "share": [3, 5], "other": [3, 11, 18], "who": 3, "requir": [3, 11, 13, 14, 16, 19, 23], "mode": 3, "cours": 3, "actual": 3, "involv": [3, 5], "text": [3, 13], "604": 3, "146": 3, "80": 3, "monitor": [3, 13], "chan": 3, "clr": 3, "bclr": 3, "align": 3, "horiz": 3, "center": 3, "limit": 3, "entri": [3, 13], "540": 3, "145": 3, "59": 3, "14": 3, "51": 3, "435": 3, "attribut": 3, "textix": 3, "right": 3, "Then": 3, "equival": 3, "autoconvert": 3, "ani": [3, 4, 5, 6, 8, 11, 12, 13, 18, 23], "detail": [3, 12, 18], "archiv": 3, "tag": [3, 7], "inherit": [3, 13], "composit": 3, "mirror": 3, "instanti": 3, "directli": 3, "paramset": 3, "its": [3, 13, 20, 23], "addit": [3, 13], "e": [3, 4, 6, 8, 9, 10, 16], "deriv": 3, "doe": [3, 5], "insert": [3, 13], "There": [3, 8, 19], "method": [3, 13], "asynportdriv": 3, "iter": 3, "member": [3, 13], "vector": 3, "asynparamset": 3, "store": [3, 13], "call": [3, 11, 13, 19], "empti": 3, "effect": [3, 7], "befor": [3, 5], "two": [3, 13], "reason": [3, 8], "primarili": 3, "throughout": 3, "find": [3, 9, 13], "child": 3, "must": [3, 13], "constructor": 3, "non": 3, "correct": [3, 8], "order": [3, 15, 19], "when": [3, 5, 8, 13, 16], "parameterdefinit": 3, "fulli": 3, "popul": [3, 13], "dl": [3, 13], "overload": 3, "adcor": 3, "asynndarraydriv": 3, "split": [3, 14, 18, 21], "asynndarraydriverparamset": 3, "ndplugindriv": 3, "trivial": 3, "test": [3, 5, 8, 14], "adsimdetector": 3, "simdetector": 3, "simdetectorparamset": 3, "adpilatu": 3, "motor": 3, "asynmotorcontrol": 3, "asynmotorcontrollerparamset": 3, "pmac": 3, "pmaccontrol": 3, "pmaccontrollerparamset": 3, "pmaccscontrol": 3, "same": [3, 5, 7, 8], "unavoid": 3, "edg": 3, "schema": [3, 13], "complic": 3, "first": [3, 13, 16], "inconsist": 3, "agre": 3, "wai": [3, 8, 21], "_rbv": 3, "suffix": [3, 13], "ad": 3, "g": 3, "pilatusdetector": 3, "first_driver_param": 3, "main": [3, 7, 20], "first_driver_param_index": 3, "append": 3, "depend": [3, 11, 13, 20, 23], "handl": [3, 5, 6, 13], "better": 3, "overridden": 3, "drvusercr": 3, "dynam": [3, 13], "perform": 3, "idea": [3, 5, 8], "being": [3, 6], "point": [3, 18], "everyth": [3, 13], "while": [3, 5], "confus": 3, "benefit": 3, "peopl": 3, "forc": 3, "cannot": [3, 13], "alongsid": 3, "extend": [3, 15, 18], "necessarili": 3, "problem": [3, 8, 11], "seem": 3, "unnecessari": 3, "restrict": 3, "clearer": 3, "explicitli": 3, "option": [3, 7, 13], "solut": 3, "resolv": [3, 8], "becaus": [3, 8, 11, 13], "framework": [3, 18], "easier": 3, "improv": [3, 5, 19], "move": 3, "function": [3, 9, 15, 19], "adeig": 3, "eigerparam": 3, "subclass": 3, "statement": 3, "asynparamtyp": 3, "slightli": 3, "simplifi": 3, "ndpluginfil": 3, "filewriterparamset": 3, "where": [3, 10, 12], "everi": [3, 6, 8], "plugin": 3, "under": [3, 6, 13, 16], "directori": [4, 13, 15], "tox": [4, 6, 9, 10, 11, 16], "static": [4, 14, 15, 16], "which": [4, 11, 12, 13, 16], "docstr": [4, 15], "document": [4, 5, 14, 16, 21], "standard": [4, 5, 14], "built": [4, 20], "html": 4, "open": [4, 5, 16], "web": 4, "browser": 4, "firefox": 4, "watch": 4, "your": [4, 5, 6, 8, 11, 13], "rebuild": 4, "whenev": 4, "reload": 4, "view": 4, "localhost": 4, "http": [4, 7, 12, 18, 23], "8000": 4, "sourc": [4, 10, 16, 18, 23], "too": [4, 13], "tell": [4, 6], "src": 4, "welcom": 5, "request": [5, 12], "through": [5, 16], "github": [5, 7, 12, 16, 18, 20, 23], "check": [5, 6, 9, 10, 11, 12, 15, 16], "file": [5, 6, 10, 18], "great": 5, "ticket": 5, "want": 5, "sure": 5, "don": [5, 13], "t": [5, 11, 13, 19], "spend": 5, "time": [5, 6, 8], "someth": [5, 12], "scope": 5, "offer": 5, "place": [5, 8, 13, 18], "ask": 5, "question": 5, "obviou": 5, "close": [5, 12], "rais": [5, 13], "librari": [5, 8, 21], "bug": 5, "free": 5, "significantli": 5, "easili": 5, "caught": 5, "remain": 5, "up": [5, 13, 14], "black": [6, 15], "flake8": [6, 15], "isort": [6, 15], "command": [6, 11], "Or": 6, "hook": 6, "git": [6, 12, 16, 23], "possibl": [6, 8, 13], "enabl": 6, "clone": 6, "repositori": [6, 8, 15], "result": 6, "repo": [6, 8], "report": [6, 9], "reformat": 6, "likewis": 6, "get": [6, 7, 8, 13, 14, 16, 20], "those": 6, "manual": 6, "json": [6, 13], "save": 6, "highlight": [6, 10], "editor": 6, "window": 6, "checklist": 7, "choos": [7, 16], "pep440": 7, "compliant": 7, "pep": 7, "python": [7, 8, 12, 16], "org": 7, "0440": 7, "go": [7, 8], "draft": 7, "click": [7, 8, 16], "suppli": 7, "chose": 7, "gener": [7, 12], "note": [7, 13, 18, 21], "review": 7, "titl": [7, 13, 15], "publish": [7, 8], "push": [7, 8], "branch": 7, "except": [7, 13], "By": [8, 13], "design": [8, 14], "tabl": [8, 13], "pyproject": 8, "toml": 8, "version": [8, 12, 13, 20, 22], "best": [8, 11], "leav": 8, "widest": 8, "rang": 8, "compat": 8, "approach": [8, 19], "break": 8, "releas": [8, 14, 18, 20, 21, 23], "issu": [8, 10], "work": [8, 21], "howev": 8, "simpli": 8, "try": 8, "minor": 8, "mechan": 8, "previou": 8, "success": 8, "quick": 8, "guarante": 8, "asset": 8, "diamondlightsourc": [8, 12], "txt": 8, "show": [8, 13], "freez": 8, "sub": 8, "download": 8, "ran": 8, "matrix": 8, "ubuntu": 8, "8": [8, 16, 23], "lockfil": 8, "root": [8, 11, 13], "renam": 8, "commit": [8, 14, 15, 16], "exactli": 8, "good": [8, 19], "back": [8, 13, 18], "unlock": 8, "earli": 8, "indic": [8, 12], "incom": 8, "restor": 8, "coverag": 9, "commandlin": [9, 23], "cov": 9, "without": 10, "potenti": 10, "match": 10, "runtim": 11, "verifi": 11, "docker": [11, 20], "fail": 11, "podman": [11, 16], "workstat": 11, "interchang": 11, "help": [11, 19], "paramet": [11, 13, 18], "merg": 12, "keep": 12, "sync": 12, "rebas": 12, "fals": 12, "com": [12, 16, 23], "conflict": 12, "area": 12, "explain": 13, "pvi": [13, 16, 20, 23], "yaml": [13, 18], "turn": 13, "softwar": [13, 19, 23], "insid": 13, "specifi": [13, 18], "dure": 13, "deserialis": 13, "later": [13, 16, 18, 23], "translat": 13, "class": 13, "scalar": 13, "str": [13, 15], "readwidget": 13, "none": 13, "blank": 13, "support": 13, "action": 13, "write_pv": 13, "pv_name": 13, "writepv": 13, "signalx": 13, "118": 13, "120": 13, "40": 13, "tooltip": 13, "extract": [13, 15], "alter": 13, "abstract": 13, "mandatori": 13, "as_discriminated_union": 13, "basetyp": 13, "def": [13, 15], "self": 13, "notimplementederror": 13, "obtain": 13, "destin": 13, "With": 13, "allow": [13, 18], "customis": 13, "placement": 13, "within": 13, "screnlayout": 13, "dataclass": 13, "import": [13, 15], "util": 13, "configur": 13, "screenlayout": 13, "space": 13, "title_height": 13, "bar": [13, 14, 21], "max_height": 13, "max": 13, "group_label_height": 13, "label_width": 13, "widget_width": 13, "widget_height": 13, "group_widget_ind": 13, "indent": 13, "group_width_offset": 13, "border": 13, "decid": 13, "referenc": 13, "adjust": 13, "anyth": 13, "els": 13, "consid": [13, 15], "screen_layout": 13, "26": 13, "relat": 13, "becuas": 13, "person": 13, "prefer": 13, "clariti": 13, "languag": 13, "server": 13, "dlsformatt": 13, "900": 13, "previous": 13, "state": 13, "overwrit": 13, "data": 13, "_format": 13, "eg": 13, "refer": [13, 19, 22], "identifi": 13, "bobtempl": 13, "__file__": 13, "achiev": 13, "screenwidget": 13, "snippet": 13, "widgetfactori": 13, "from_templ": 13, "widget_formatter_factori": 13, "widgetformatterfactori": 13, "header_formatter_cl": 13, "labelwidgetformatt": 13, "search": 13, "head": [13, 15], "property_map": 13, "dict": 13, "label_formatter_cl": 13, "led_formatter_cl": 13, "pvwidgetformatt": 13, "bound": 13, "squar": 13, "progress_bar_formatter_cl": 13, "text_read_formatter_cl": 13, "check_box_formatter_cl": 13, "choicebutton": 13, "combo_box_formatter_cl": 13, "text_write_formatter_cl": 13, "textentri": 13, "table_formatter_cl": 13, "action_formatter_cl": 13, "actionwidgetformatt": 13, "actionbutton": 13, "sub_screen_formatter_cl": 13, "subscreenwidgetformatt": 13, "subscreen": 13, "file_nam": 13, "uniqu": 13, "term": 13, "locat": 13, "extrac": 13, "irrelev": 13, "greatli": 13, "rectangl": 13, "behind": 13, "collect": 13, "dedic": 13, "argument": 13, "posit": 13, "screen_title_cl": 13, "group_title_cl": 13, "create_group_object_formatt": 13, "widgetformatt": 13, "return": [13, 15], "f": 13, "create_screen_title_formatt": 13, "layoutproperti": 13, "readi": 13, "formatter_factori": 13, "screenformatterfactori": 13, "screen_formatter_cl": 13, "groupformatt": 13, "grouptyp": 13, "with_titl": 13, "widget_formatter_hook": 13, "group_formatter_cl": 13, "base_file_nam": 13, "stem": 13, "screen_cl": 13, "group_cl": 13, "separ": 13, "groupfactori": 13, "make_widget": 13, "itself": 13, "kei": 13, "calcul": [13, 22], "uniform": 13, "On": 13, "chosen": 13, "screen_formatt": 13, "sub_screen": 13, "create_screen_formatt": 13, "write_bob": 13, "sub_screen_nam": 13, "sub_screen_formatt": 13, "sub_screen_path": 13, "left": 13, "step": [13, 14, 16, 21], "unpack": 13, "alwai": 13, "et": 13, "etre": 13, "fromstr": 13, "tostr": 13, "grid_step_i": 13, "getroottre": 13, "pretty_print": 13, "thats": 13, "complet": 13, "both": 13, "5": 13, "25": 13, "115": 13, "format_edl": 13, "elif": 13, "format_bob": 13, "valueerror": 13, "edltempl": 13, "read_text": 13, "controlpv": 13, "indicatorpv": 13, "onlabel": 13, "offlabel": 13, "subscreenfil": 13, "displayfilenam": 13, "group_box_cl": 13, "fillcolor": 13, "create_group_box_formatt": 13, "write_text": 13, "join": 13, "lp": 13, "ref": 13, "sw": 13, "screen_ini": 13, "screen_format": 13, "four": [14, 19, 21], "categori": [14, 21], "side": [14, 21], "contribut": [14, 18], "sphinx": [14, 15, 16], "pytest": [14, 16], "analysi": [14, 15, 16], "mypi": [14, 15, 16], "pre": [14, 15, 16, 20], "pin": 14, "practic": [14, 21], "dai": 14, "dev": [14, 16], "task": 14, "architectur": 14, "decis": 14, "origin": 14, "driver": [14, 18], "why": [14, 21], "technic": [14, 19, 21], "materi": [14, 21], "conform": 15, "how": [15, 19], "napoleon": 15, "extens": 15, "googl": 15, "signatur": 15, "func": 15, "arg1": 15, "arg2": 15, "bool": 15, "summari": 15, "arg": 15, "underlin": 15, "convent": 15, "headl": 15, "instruct": 16, "minim": 16, "epic": [16, 18, 20, 23], "host": 16, "machin": 16, "vscode": 16, "virtualenv": 16, "m": [16, 23], "bin": [16, 23], "activ": [16, 23], "devcontain": 16, "reopen": 16, "prompt": 16, "termin": [16, 23], "complex": 16, "graph": 16, "pipdeptre": 16, "parallel": 16, "target": 18, "streamdevic": 18, "templat": 18, "pypi": 18, "io": [18, 20], "propos": 18, "subject": 18, "present": 18, "tens": 18, "prototyp": 18, "grand": 19, "unifi": 19, "theori": 19, "david": 19, "la": 19, "secret": 19, "understood": 19, "isn": 19, "tutori": 19, "explan": 19, "purpos": 19, "understand": 19, "implic": 19, "often": 19, "immens": 19, "topic": 19, "alreadi": 20, "registri": 20, "ghcr": 20, "typic": 21, "usag": 21, "experienc": 21, "intern": 22, "__version__": 22, "noindex": 22, "pypa": 22, "setuptools_scm": 22, "recommend": 23, "interfer": 23}, "objects": {"": [[22, 0, 0, "-", "pvi"]]}, "objtypes": {"0": "py:module"}, "objnames": {"0": ["py", "module", "Python module"]}, "titleterms": {"architectur": [0, 1], "decis": [0, 1, 2], "record": [0, 1], "1": 1, "statu": [1, 2], "context": [1, 2], "consequ": [1, 2], "2": 2, "adopt": 2, "python3": 2, "pip": 2, "skeleton": 2, "project": [2, 5], "structur": [2, 18], "origin": 3, "design": 3, "aim": 3, "pvi": [3, 18, 22], "how": [3, 13, 14, 18, 21], "work": 3, "yaml": 3, "file": [3, 8, 13], "screen": [3, 13], "html": 3, "document": [3, 15, 18, 19], "pilatu": 3, "paramet": 3, "question": 3, "One": 3, "time": 3, "gener": [3, 13], "check": [3, 23], "sourc": 3, "control": 3, "makefil": 3, "which": 3, "tool": [3, 12], "support": [3, 6], "driver": 3, "databas": 3, "templat": [3, 13], "ui": 3, "ongo": 3, "develop": [3, 5, 14, 16], "With": 3, "without": 3, "class": 3, "hierarchi": 3, "chang": 3, "summari": 3, "caveat": 3, "next": 3, "step": 3, "possibl": 3, "further": 3, "build": [4, 11, 16], "doc": 4, "us": [4, 6, 9, 10], "sphinx": 4, "autobuild": 4, "contribut": 5, "issu": [5, 6], "discuss": 5, "code": [5, 15], "coverag": 5, "guid": [5, 14, 21], "run": [6, 9, 10, 20], "lint": 6, "pre": 6, "commit": 6, "fix": 6, "vscode": 6, "make": 7, "releas": 7, "pin": 8, "requir": 8, "introduct": 8, "find": 8, "lock": 8, "appli": 8, "remov": 8, "depend": [8, 16], "from": 8, "ci": 8, "test": [9, 11, 16], "pytest": 9, "static": 10, "analysi": 10, "mypi": 10, "contain": [11, 20], "local": 11, "updat": 12, "write": 13, "site": 13, "specif": 13, "formatt": 13, "overview": 13, "creat": [13, 23], "subclass": 13, "defin": 13, "layout": 13, "properti": 13, "assign": 13, "divid": 13, "widget": 13, "group": 13, "function": 13, "construct": 13, "object": 13, "tutori": [14, 21], "explan": [14, 21], "refer": [14, 21], "standard": 15, "instal": [16, 23], "clone": 16, "repositori": 16, "see": 16, "what": 16, "wa": 16, "api": [17, 22], "index": 17, "i": 18, "about": 19, "start": 20, "user": 21, "your": 23, "version": 23, "python": 23, "virtual": 23, "environ": 23, "librari": 23}, "envversion": {"sphinx.domains.c": 2, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 8, "sphinx.domains.index": 1, "sphinx.domains.javascript": 2, "sphinx.domains.math": 2, "sphinx.domains.python": 3, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx.ext.intersphinx": 1, "sphinx.ext.viewcode": 1, "sphinx": 57}, "alltitles": {"Architectural Decision Records": [[0, "architectural-decision-records"]], "1. Record architecture decisions": [[1, "record-architecture-decisions"]], "Status": [[1, "status"], [2, "status"]], "Context": [[1, "context"], [2, "context"]], "Decision": [[1, "decision"], [2, "decision"]], "Consequences": [[1, "consequences"], [2, "consequences"]], "2. Adopt python3-pip-skeleton for project structure": [[2, "adopt-python3-pip-skeleton-for-project-structure"]], "Original Design": [[3, "original-design"]], "Aims of PVI": [[3, "id1"]], "How it works": [[3, "how-it-works"]], "YAML file": [[3, "yaml-file"]], "Screen files": [[3, "screen-files"]], "HTML Documentation": [[3, "html-documentation"]], "Pilatus Parameters": [[3, "id2"]], "Questions": [[3, "questions"]], "One-time generation and checked into source control or generated by Makefile?": [[3, "one-time-generation-and-checked-into-source-control-or-generated-by-makefile"]], "Which screen tools to support?": [[3, "which-screen-tools-to-support"]], "Drivers": [[3, "drivers"]], "Database Template File": [[3, "database-template-file"]], "UI": [[3, "ui"]], "Ongoing Development": [[3, "ongoing-development"]], "With PVI": [[3, "with-pvi"]], "Without PVI": [[3, "without-pvi"]], "Class Hierarchy": [[3, "class-hierarchy"]], "Change Summary": [[3, "change-summary"]], "Caveats": [[3, "caveats"]], "Next Steps": [[3, "next-steps"]], "Possible Further Work": [[3, "possible-further-work"]], "Build the docs using sphinx": [[4, "build-the-docs-using-sphinx"]], "Autobuild": [[4, "autobuild"]], "Contributing to the project": [[5, "contributing-to-the-project"]], "Issue or Discussion?": [[5, "issue-or-discussion"]], "Code coverage": [[5, "code-coverage"]], "Developer guide": [[5, "developer-guide"]], "Run linting using pre-commit": [[6, "run-linting-using-pre-commit"]], "Running pre-commit": [[6, "running-pre-commit"]], "Fixing issues": [[6, "fixing-issues"]], "VSCode support": [[6, "vscode-support"]], "Make a release": [[7, "make-a-release"]], "Pinning Requirements": [[8, "pinning-requirements"]], "Introduction": [[8, "introduction"]], "Finding the lock files": [[8, "finding-the-lock-files"]], "Applying the lock file": [[8, "applying-the-lock-file"]], "Removing dependency locking from CI": [[8, "removing-dependency-locking-from-ci"]], "Run the tests using pytest": [[9, "run-the-tests-using-pytest"]], "Run static analysis using mypy": [[10, "run-static-analysis-using-mypy"]], "Container Local Build and Test": [[11, "container-local-build-and-test"]], "Update the tools": [[12, "update-the-tools"]], "How to Write a Site Specific Formatter": [[13, "how-to-write-a-site-specific-formatter"]], "Overview": [[13, "overview"]], "Create a formatter subclass": [[13, "create-a-formatter-subclass"]], "Define the Screen Layout Properties": [[13, "define-the-screen-layout-properties"]], "Assign a Template File": [[13, "assign-a-template-file"]], "Divide the Template into Widgets": [[13, "divide-the-template-into-widgets"]], "Define screen and group widget functions": [[13, "define-screen-and-group-widget-functions"]], "Construct a Screen Object": [[13, "construct-a-screen-object"]], "Generate the Screen file": [[13, "generate-the-screen-file"]], "Developer Guide": [[14, "developer-guide"]], "Tutorials": [[14, null], [21, null]], "How-to Guides": [[14, null], [21, null]], "Explanations": [[14, null], [21, null]], "Reference": [[14, null], [21, null]], "Standards": [[15, "standards"]], "Code Standards": [[15, "code-standards"]], "Documentation Standards": [[15, "documentation-standards"]], "Developer install": [[16, "developer-install"]], "Clone the repository": [[16, "clone-the-repository"]], "Install dependencies": [[16, "install-dependencies"]], "See what was installed": [[16, "see-what-was-installed"]], "Build and test": [[16, "build-and-test"]], "API Index": [[17, "api-index"]], "PVI": [[18, "pvi"]], "How the documentation is structured": [[18, "how-the-documentation-is-structured"]], "About the documentation": [[19, "about-the-documentation"]], "Run in a container": [[20, "run-in-a-container"]], "Starting the container": [[20, "starting-the-container"]], "User Guide": [[21, "user-guide"]], "API": [[22, "module-pvi"]], "pvi": [[22, "pvi"]], "Installation": [[23, "installation"]], "Check your version of python": [[23, "check-your-version-of-python"]], "Create a virtual environment": [[23, "create-a-virtual-environment"]], "Installing the library": [[23, "installing-the-library"]]}, "indexentries": {"module": [[22, "module-pvi"]], "pvi": [[22, "module-pvi"]]}})