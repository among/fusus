URLS=[
"fusus/index.html",
"fusus/clean.html",
"fusus/lib.html",
"fusus/layout.html",
"fusus/tfFromTsv.html",
"fusus/convert.html",
"fusus/works.html",
"fusus/lakhnawi.html",
"fusus/char.html",
"fusus/page.html",
"fusus/pdf.html",
"fusus/about/index.html",
"fusus/about/model.html",
"fusus/about/sources.html",
"fusus/about/install.html",
"fusus/about/rationale.html",
"fusus/about/howto.html",
"fusus/lines.html",
"fusus/ocr.html",
"fusus/parameters.html",
"fusus/book.html"
];
INDEX=[
{
"ref":"fusus",
"url":0,
"doc":"![logo](images/fusus-small.png)  Fusus Pipeline A pipe line from Arabic printed books to structured textual data. With the results of this pipeline researchers can study the commentary tradition based on Ibn Arabi's Fusus Al Hikam (Bezels of Wisdom).  Straight to  .  Install ( fusus.about.install )  HowTo ( fusus.about.howto )  Sources ( fusus.about.sources )  Rationale ( fusus.about.rationale )  Authors  [Cornelis van Lit](https: digitalorientalist.com/about-cornelis-van-lit/)  [Dirk Roorda](https: www.annotation.nl)  Project Fusus has been funded by the IT Research Innovation Fund. It has been developed between 2020-03-01 and 2021-03-01"
},
{
"ref":"fusus.clean",
"url":1,
"doc":"Wipe marks from images. Cleaning marks from images is based on [OpenCV's template matching](https: opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html template-matching) This is fuzzy matching, so we have to employ considerable sophistication to get the true results and to discard the fake results. One particular way to discard fake results is to mind the connectedness of the ink of a candidate mark with the surrounding ink. If there is such a connection, it is a strong indication that the candidate is not a mark to be removed, but part of a glyph. See ![bordering](images/isolation.png)"
},
{
"ref":"fusus.clean.cluster",
"url":1,
"doc":"Cluster points that are in a source. When searching images for image templates, we get a match image: for each point in the image a measure of how good the match is at that point. Typically, if a point has a high match value, surrounding points also have good match values. We want to cluster such points, so that we can identify a match with exactly one cluster. Parameters      points: iterable Points where the image template matches the source image good enough match: image as np array The match image Returns    - list The list of clusters, where each cluster is represented as a pair of point and the strength of the match in that point. This point is the point in the cluster with the highest match value.",
"func":1
},
{
"ref":"fusus.clean.measure",
"url":1,
"doc":"Measure the amount of ink that crosses the border of a certain region. It is used to reject certain matches of image templates, where templates contain strokes of ink. If a match is such that the stroke of ink connects with the ink in the environment, the match is not a true example of the stroke and will be rejected.  ! note \"Where to look for ink\" We look for ink in the image itself, the ink in the search template is not relevant. Parameters      borderInside: image as np array The part of the image bordering inside an area where the search template matches borderOutside: image as np array The part of the image bordering outside an area where the search template matches Returns    - float The ratio between the size of the ink connections across the border and the total size of the border.",
"func":1
},
{
"ref":"fusus.clean.connected",
"url":1,
"doc":"Determine how much ink borders on a given rectangle. Parameters      markH: integer height of the rectangle markW: integer width of the rectangle bw: integer width of the border around the rectangle that will be used to detect connections threshold: the value above which a connection is detected img: np array the source image hitPoint: (int, int) Y and X coordinate of top left corner of the rectangle in the image sides: string, optional  None If  None , computes connections on all sides. Otherwise it should be a string consisting of at most these characters:  l (left),  r (right),  t (top),  b (bottom). Only these sides will be computed.",
"func":1
},
{
"ref":"fusus.clean.reborder",
"url":1,
"doc":"Add a border around a grayscale image, optionally remove white margins first. The border will add to the size of the image. Parameters      gray: np array A grayscale image. bw: int Width of the new border. color: int Color of the new border (grayscale). crop: boolean, optional  False If  True , the image will be cropped first such as to remove all surrounding white margins.",
"func":1
},
{
"ref":"fusus.clean.addBox",
"url":1,
"doc":"Add a box around a mark that is to be cleaned. When we display the marks that will be wiped from the image, we do so by putting colored boxes around them. This function adds one such box. Parameters C: object The configuration object of the book engine. img: image as np array the image to operate on left, top, right, bottom: int specification of the rectangle of the box kept: boolean Whether the mark is to be kept. Kept marks and wiped marks will get different colors. band: string The name of the band in which the mark is searched for. It will be displayed near the box. seq: integer The number of the mark. connDegree: integer The degree of ink connection for this mark occurrence. It will be displayed near the box. Returns    - None The source image receives a modification.",
"func":1
},
{
"ref":"fusus.lib",
"url":2,
"doc":""
},
{
"ref":"fusus.lib.pprint",
"url":2,
"doc":"",
"func":1
},
{
"ref":"fusus.lib.dh",
"url":2,
"doc":"",
"func":1
},
{
"ref":"fusus.lib.EXTENSIONS",
"url":2,
"doc":"Supported image file extensions."
},
{
"ref":"fusus.lib.parseNums",
"url":2,
"doc":"Parses a value as one or more numbers. Parameters      numSpec: None | int | string | iterable If  None results in  None . If an  int , it stands for that int. If a  string , it is allowed to be a comma separated list of numbers or ranges, where a range is a lower bound and an upper bound separated by a  - . If none of these, it should be an iterable of  int values. Examples: 50 \"50\" \"50,70\" \"50-70,91,92,300-350\" (50, 70, 91, 92, 300) [50, 70, 90] range(300, 350) Returns    - None | iterable of int Depending on the value.",
"func":1
},
{
"ref":"fusus.lib.getNbLink",
"url":2,
"doc":"",
"func":1
},
{
"ref":"fusus.lib.getNbPath",
"url":2,
"doc":"",
"func":1
},
{
"ref":"fusus.lib.tempFile",
"url":2,
"doc":"Get a temporary file.",
"func":1
},
{
"ref":"fusus.lib.imgElem",
"url":2,
"doc":"Produce an image with its data packaged into a HTML  element.",
"func":1
},
{
"ref":"fusus.lib.PILFromArray",
"url":2,
"doc":"",
"func":1
},
{
"ref":"fusus.lib.arrayFromPIL",
"url":2,
"doc":"",
"func":1
},
{
"ref":"fusus.lib.showImage",
"url":2,
"doc":"Show one or more images.",
"func":1
},
{
"ref":"fusus.lib.writeImage",
"url":2,
"doc":"Write an image to disk",
"func":1
},
{
"ref":"fusus.lib.overlay",
"url":2,
"doc":"Colors a region of an image with care. A selected region of an image can be given a uniform color, where only pixels are changed that have an exact given color. In this way you can replace all the white with gray, for example, without wiping out existing non-white pixels. Parameters      img: np array The image to be overlain with a new color (left, top, right, bottom): (int, int, int, int) The region in the image to be colored srcColor: RGB color The color of the pixels that may be replaced. dstColor: The new color of the replaced pixels.",
"func":1
},
{
"ref":"fusus.lib.splitext",
"url":2,
"doc":"Splits a file name into its main part and its extension. Parameters      f: string The file name withDot: boolean, optional  False If True, the  . in the extension is considered part of the extension, else the dot is stripped from it. Returns    - tuple The main part and the extension",
"func":1
},
{
"ref":"fusus.lib.imageFileList",
"url":2,
"doc":"Gets a sorted list of image files from a directory. Only files having an image extension (defined in  EXTENSIONS ) are listed. Parameters      imDir: string Path to the image directory Returns    - list Alphabetically sorted list of file names (without directory, with extension)",
"func":1
},
{
"ref":"fusus.lib.imageFileListSub",
"url":2,
"doc":"Gets sorted lisst of image files from the subdirectories of a directory. Only files having an image extension (defined in  EXTENSIONS ) are listed. Parameters      imDir: string Path to the image directory Returns    - dict Keyed by subdirectory names, valued by alphabetically sorted list of file names (without directory, with extension)",
"func":1
},
{
"ref":"fusus.lib.pagesRep",
"url":2,
"doc":"Represents a set of pages as a string in a compact way or as a list. Parameters      source: list A list of file names, without directory, with extension asList: boolean, optional  False Whether to return the result as a list of integers or as a compact string. Returns    - list or string Depending on  asList a list of page numbers (integers) or a string mentioning the page numbers, using intervals where possible.",
"func":1
},
{
"ref":"fusus.lib.select",
"url":2,
"doc":"Choose items from a bunch of integers. Parameters      source: iterable of int The items to choose from selection: iterable of int or string or  None If None, selects all items, otherwise specifies what numbers to select. If a number is in the selection, but not in the source, it will not be selected. The selection can be an integer or a compact string that specifies integers, using ranges and commas. Returns    - list Sorted list of selected items",
"func":1
},
{
"ref":"fusus.lib.cropBorders",
"url":2,
"doc":"Get the bounding box of the image without black borders, if any. The image is white writing on black background. The outer frame is white, if any. We find the region within a white outer frame by identifying all black pixels and computing a bounding box around it. Thanks to [stackoverflow](https: codereview.stackexchange.com/a/132933). Parameters      img: numpy array The image. We assume it is grayscale, and inverted. For best results, it should be blurred before thresholding. tolerance: integer This parameter is the upper limit of what counts as black. Returns    - int, int, int, int The (x0, x1, y0, y1) of the crop region. This will be used in  removeBorders to whiten the margins outside it.",
"func":1
},
{
"ref":"fusus.lib.removeBorders",
"url":2,
"doc":"Remove black borders around an image. When an image has been unskewed, sharp triangle-shape strokes in the corners may have been introduced. Or it might be the result of scanning a page. This function removes them by coloring all image borders with white. The exact borders to be whitened are calculated by  cropBorders . Parameters      img: image as np array the image to operate on crop: (int, int, int, int) the x1, x2, y1, y2 values which indicate the region outside which the white may be applied white: color the exact white color with which we color the borders. Returns    - None The source image receives a modification.",
"func":1
},
{
"ref":"fusus.lib.parseStages",
"url":2,
"doc":"Parses a string that specifies stages. Stages are steps in the image processing. Each stage has an intermediate processing result. Parameters      stage: string or None or iterable If None: it means all stages. If a string: the name of a stage. If an iterable: the items must be names of stages. allStages: tuple Names of all stages. sortedStages: Sorted list of all stages. error: function Method to write error messages. Returns    - tuple The stages as parsed.",
"func":1
},
{
"ref":"fusus.lib.parseBands",
"url":2,
"doc":"Parses a string that specifies bands. Bands are horizontal rectangles defined with respect to lines. They correspond with regions of interest where we try to find specific marks, such as commas and accents. Parameters      band: string or None or iterable If None: it means all bands. If a string: the name of a band. If an iterable: the items must be names of bands. allBands: tuple Names of all bands. error: function Method to write error messages. Returns    - tuple The bands as parsed.",
"func":1
},
{
"ref":"fusus.lib.parseMarks",
"url":2,
"doc":"Parses a string that specifies Marks. Marks are strokes that we need to find on the page in order to remove them. They are organized in bands: the regions of interest with respect to the lines where we expect them to occur. Parameters      mark: string or None or iterable If None: it means all marks. If a string: the name of a mark. If an iterable: the items must be names of marks. allMarks: tuple Names of all marks. error: function Method to write error messages. Returns    - tuple The marks as parsed.",
"func":1
},
{
"ref":"fusus.lib.findRuns",
"url":2,
"doc":"Find runs of consecutive items in an array. Credits: [Alistair Miles](https: gist.github.com/alimanfoo/c5977e87111abe8127453b21204c1065)",
"func":1
},
{
"ref":"fusus.lib.applyBandOffset",
"url":2,
"doc":"Produce bands from a list of lines. Bands are defined relative to lines by means of offsets of the top and bottom heights of the lines. Bands may also be interlinear: defined between the bottom of one line and the top of the next line. Parameters      C: object Configuration settings height: The height of the page or block bandName: string The name of the bands lines: tuple The lines relative to which the bands have to be determined. Lines are given as a tuple of tuples of top and bottom heights. inter: boolean, optional  False Whether the bands are relative the lines, or relative the interlinear spaces. Returns    - tuple For each line the band named bandName specified by top and bottom heights.",
"func":1
},
{
"ref":"fusus.lib.getMargins",
"url":2,
"doc":"Get margins from a histogram. The margins of a histogram are the coordinates where the histogram reaches a threshold for the first time and for the last time. We deliver the pairs (0, xFirst) and (xLast, maxWidth) if there are points above the threshold, and (0, maxW) otherwise. Parameters      hist: [int] Source array of pixel values width: int Maximum index of the source array threshold: int Value below which pixels count as zero",
"func":1
},
{
"ref":"fusus.lib.pureAverage",
"url":2,
"doc":"Get the average of a list of values after removing the outliers. It is used for calcaluting lineheights from a sequence of distances between histogram peaks. In practice, some peaks are missing due to short line lengths, and that causes some abnormal peak distances which we want to remove. Parameters      data: np array The list of values whose average we compute. supplied: integer Value to return if there is no data.",
"func":1
},
{
"ref":"fusus.layout",
"url":3,
"doc":"Detect the page layout. Pages consist of a header region, a body region, and a footer region, all of which are optional.  header The header consists of a caption and/or a page number. All headers will be discarded.  footer The footer consists of footnote bodies. All footers will be discarded.  body The body region consists of zero or more  stripes .  stripe, column, block, line A stripe is a horizontal region of the body. If some parts of the body have two columns and other parts have one column, we divide the body in stripes where each stripe has a fixed number of columns, and neighbouring stripes have a different number of columns. If the whole body has the same number of columns, we have just one stripe. The stripes are numbered 1, 2, 3,  . from top to bottom. The column is the empty string if a stripe has just one column, otherwise it is  l for the left column and  r for the right column. We assume that all stripes on all pages have at most two columns. A column within a stripe is also called a  block . Blocks are divided into  lines . The lines are numbered with the blocks that contain them."
},
{
"ref":"fusus.layout.addBlockName",
"url":3,
"doc":"Adds the name of a block of the page near the block. The function  fusus.page.Page.doLayout divides the page into blocks. This function puts the name of each block on the image, positioned suitably w.r.t. the block. Parameters      img: image as np array the image to operate on top, left, right: integer Where the top, left, right edges of the image are. marginX: integer Where we set the left margin letterColor: color The color of the letters stripe: integer The stripe number. Stripes are horizontal page-wide regions corresponding to  vertical column dividers. kind: string Whether the block spans the whole page width (   ), is in the left column (\"l\") or in the right column (\"r\"). size: float The font-size of the letters. Returns    - None The source image receives a modification.",
"func":1
},
{
"ref":"fusus.layout.addHStroke",
"url":3,
"doc":"Marks a detected horizontal stroke on an image. The layout algorithm detects horizontal strokes. For feedback to the user, we draw a frame around the detected strokes and give them a name. Parameters      img: image as np array the image to operate on isTop: boolean whether the stroke separates the top header from the rest of the page. i: integer The number of the stroke column: string {\"l\", \"r\",  } The column in which the stroke is found thickness: integer The thickness of the stroke as found on the image. top, left, right: integer Where the top, left, right edges of the image are. letterColor: color The color of the letters size: float The font-size of the letters. Returns    - None The source image receives a modification.",
"func":1
},
{
"ref":"fusus.layout.getStretches",
"url":3,
"doc":"Gets significant horizontal or vertical strokes. Significant strokes are those that are not part of letters, but ones that are used as separators, e.g. of footnotes and columns. We single out 1-pixel wide lines longer than a small threshold in the appropriate direction, and blacken the rest. Then we blur in the perpendicular direction. Now we single out longer 1-pixel wide lines and cluster in the perpendicular direction. Clusters are line segments with nearly the same constant coordinate. If we do horizontal lines, clusters are pairs of x coordinates for one y coordinate. If we do vertical lines, clusters are pairs of y coordinates for one x coordinate. We return the clusters, i.e. a dict keyed by the fixed coordinate and valued by the pair of segment coordinates. Parameters      C: object The configuration object of the book engine. info: function To write messages to the console stages: dict Intermediate cv2 images, keyed by stage name pageSize: int The width or height in pixels of a complete page. Note that the image we work with, might be a fraction of a page horizontal: boolean Whether we do horizontal of vertical lines. batch: boolean Whether we run in batch mode. Returns    - dict Per fixed coordinate the list of line segments on that coordinate. A line segment is specified by its begin and end values and the thickness of the cluster it is in.",
"func":1
},
{
"ref":"fusus.layout.getStripes",
"url":3,
"doc":"Infer horizontal stripes from a set of vertical bars. A vertical bar defines a stripe on the page, i.e. a horizontal band that contains that bar. Between the vertical bars there are also stripes, they are undivided stripes. We assume the vertical bars split the page in two portions, and not more, and that they occur more or less in the middle of the page. If many vertical bars have been detected, we sort them by y1 ascending and then y2 descending and then by x. We filter the bars: if the last bar reached to y = height, we only consider bars that start lower than height.  ! note \"Fine tuning needed later on\" The vertical strokes give a rough estimate: it is possible that they start and end in the middle of the lines beside them. We will need histograms for the fine tuning. Parameters      stages: dict We need access to the normalized stage to get the page size. stretchesV: dict Vertical line segments per x-coordinate, as delivered by  getStretches . Returns    - list A list of stripes, specified as (x, y1, y2) values, where the y-coordinates y1 and y2 specify the vertical extent of the stripe, and x is the x coordinate of the dividing vertical stroke if there is one and  None otherwise.",
"func":1
},
{
"ref":"fusus.layout.getBlocks",
"url":3,
"doc":"Fine-tune stripes into blocks. We enlarge the stripes vertically by roughly a line height and call  adjustVertical to get precise vertical demarcations for the blocks at both sides of the stripe if there is one or else for the undivided stripe. The idea is: If a stripe has a vertical bar, we slightly extend the boxes left and right so that the top and bottom lines next to the bar are completely included. If a stripe has no vertical bar, we shrink the box so that partial top and bottom lines are delegated to the boxes above and below. We only shrink if the box is close to the boxes above or below. We do not grow boxes across significant horizontal strokes. We write the box layout unto the  layout layer. Parameters      C: object Configuration settings stages: dict We need access to several intermediate results. pageH: int The height of a full page in pixels (the image might be a fraction of a page) stripes: list The preliminary stripe division of the page, as delivered by  getStripes . stretchesH: list The horizontal stretches across which we do not shrink of enlarge batch: boolean Whether we run in batch mode. Returns    - dict Blocks keyed by stripe number and column specification (one of    ,  \"l\" ,  \"r\" ). The values form dicts themselves, with in particular the bounding box information under key  box specified as four numbers: left, top, right, bottom. The dict is ordered.",
"func":1
},
{
"ref":"fusus.layout.applyHRules",
"url":3,
"doc":"Trims regions above horizontal top lines and below bottom lines. Inspect the horizontal strokes and specifiy which ones are top separators and which ones are bottom separators. First we map each horizontal stretch to one of the page stripes. If a stretch occurs between stripes, we map it to the stripe above. A horizontal stroke is a top separator if  it is mapped to the first stripe  and  it is situated in the top fragment of the page. We mark the discarded material on the layout page by overlaying it with gray. Parameters      C: object Configuration settings stages: dict We need access to several intermediate results. stretchesH: dict Horizontal line segments per y-coordinate, as delivered by  getStretches . stripes: list The preliminary stripe division of the page, as delivered by  getStripes . blocks: dict The blocks as delivered by  getBlocks . boxed: boolean Whether we run in boxed mode (generate boxes around wiped marks). Returns    - None The blocks dict will be updated: each block value gets a new key  inner with the bounding box info after stripping the top and bottom material.",
"func":1
},
{
"ref":"fusus.layout.grayInterBlocks",
"url":3,
"doc":"Overlay the space between blocks with gray. Remove also the empty blocks from the block list. Parameters      C: object Configuration settings stages: dict We need access to several intermediate results. blocks: dict The blocks as delivered by  getBlocks . The blocks dict will be updated: empty blocks will be deleted from it. with the band data. Returns    - None.",
"func":1
},
{
"ref":"fusus.layout.adjustVertical",
"url":3,
"doc":"Adjust the height of blocks. When we determine the vertical sizes of blocks from the vertical column separators on the page, we may find that these separators are too short. We remedy this by finding the line divisision of the ink left and right from the dividing line, and enlarging the blocks left and right so that they contain complete lines. Parameters      C: object Configuration settings info: function To write messages to the console blurred: image as np array The input image. It must be the  blurred stage of the source image, which is blurred and inverted. pageH: int size of a full page in pixels left, right: int The left and right edges of the block yMin: integer the initial top edge of the block yMinLee: integer the top edge of the block when the leeway is applied yMax: integer the initial bottom edge of the block yMaxLee: integer the bottom edge of the block when the leeway is applied preferExtend: boolean Whether we want to increase or rather decrease the vertical size of the block. Blocks next to dividing lines are meant to be increased, blocks that span the whole page width are meant to be decreased. Returns    - tuple The corrected top and bottom heights of the block.",
"func":1
},
{
"ref":"fusus.tfFromTsv",
"url":4,
"doc":"Convert TSV data to Text-Fabric. The TSV data consists of one-word-per-line files for each page, and for each word the line specifies its text, its bounding boxes in the original, and its containing spaces on the page (line, block, etc). The TSV data from OCRed pages is slightly different from that of the textual extraction of the Lakhnawi PDF, but they share most fields. The code here can deal with both kinds of input. See also   fusus.convert  [Text-Fabric](https: annotation.github.io/text-fabric/tf/index.html)"
},
{
"ref":"fusus.tfFromTsv.generic",
"url":4,
"doc":"",
"func":1
},
{
"ref":"fusus.tfFromTsv.getToc",
"url":4,
"doc":"",
"func":1
},
{
"ref":"fusus.tfFromTsv.convert",
"url":4,
"doc":"",
"func":1
},
{
"ref":"fusus.tfFromTsv.director",
"url":4,
"doc":"Read tsv data fields. Fields are integer valued, except for fields with names ending in $. If a row comes from the result of OCR we have the fields:   stripe block$ line left top right bottom confidence text$   We prepend the page number in this case, yielding   page stripe block$ line left top right bottom confidence text$   Otherwise we have:   page line column span direction$ left top right bottom text$   See  fusus.lakhnawi.Lakhnawi.tsvPages . The block in an OCRed file is either  r or  l or nothing, it corresponds to material to the left and right of a vertical stroke. If there is no vertical stroke, there is just one block. The column in a non OCRed file is either  1 or  2 and comes from a line partitioned into two regions by means of white space. In both cases, the first 4 fields denote a sectional division in the words.",
"func":1
},
{
"ref":"fusus.tfFromTsv.loadTf",
"url":4,
"doc":"",
"func":1
},
{
"ref":"fusus.convert",
"url":5,
"doc":"Convenience methods to call conversions to and from tsv and to tf. The pipeline can read Arabic books in the form of page images, and returns structured data in the form of tab separated files.  Books As far as the pipeline is concerned, the input of a book is a directory of page images. More precisely, it is a directory in which there is a subdirectory  in having the page images. The books of the Fusus project are in the directory  ur of this repo. There you find subdirectories corresponding to   Affifi The Fusus Al Hikam in the Affifi edition.   Lakhnawi The Fusus Al Hikam in the Lakhnawi edition. The source is a textual PDF, not in the online repo, from which structured data is derived by means of a specific workflow, not the  pipeline .   commentary Xxx Commentary books When the pipeline runs, it produces additional directories containing intermediate results and output. For details, see  fusus.works ,  fusus.book , and  fusus.lakhnawi . All functions here make use of  fusus.works , which makes it possible to refer to known works by keywords. If you want to process other works, that is still possible, just provide directories where source keywords are expected. It is assumed that unknown works use the OCR pipeline. If that is not true, pass a parameter  ocred=False to the function, or, on the command line, pass  noocr .  Run You can run the pipeline on the known works inside the  ur directory in this repo or on books that you provide yourself. This script supports one-liners on the command line to execute the pipeline and various conversion processes. See  fusus.convert.HELP .  Load TSV The function  loadTsv to load TSV data in memory. For known works, it will also convert the data types of the appropriate fields to integer."
},
{
"ref":"fusus.convert.HELP",
"url":5,
"doc":" text Convert tsv data files to TF and optionally loads the TF. python3 -m fusus.convert  help python3 -m fusus.convert tsv source ocr|noocr pages python3 -m fusus.convert tf source ocr|noocr pages versiontf [load] [loadonly]  help: print this text and exit source : a work (given as keyword or as path to its work directory) Examples: fususl (Fusus Al Hikam in Lakhnawi edition) fususa (Fusus Al Hikam in Affifi edition) any commentary by its keyword ~/github/myorg/myrepo/mydata mydir/mysubdir pages : page specification, only process these pages; default: all pages Examples: 50 50,70 50-70,91,92,300-350 ocr : assume the work is in the OCR pipeline noocr : assume the work is not in the OCR pipeline (it is then a text extract from a pdf) For tf only: versiontf : loads the generated TF; if missing this step is not performed Examples: 0.4 3.7.2 load : loads the generated TF; if missing this step is not performed loadOnly : does not generate TF; loads previously generated TF  "
},
{
"ref":"fusus.convert.makeTf",
"url":5,
"doc":"Make Text-Fabric data out of the TSV data of a work. The work is specified either by the name of a known work (e.g.  fususa ,  fususl ) or by specifying the work directory. The function needs to know whether the tsv comes out of an OCR process or from the text extraction of a PDF. In case of a known work, this is known and does not have to be specified. Otherwise you have to pass it. Parameters      versionTf: string A version number for the TF to be generated, e.g.  0.3 . Have a look in the fusus tf subdirectory, and see which version already exists, and then choose a higher version if you do not want to overwrite the existing version. source: string, optional  None The key of a known work, see  fusus.works.WORKS . Or else the path to directory of the work. ocred: string Whether the tsv is made by the OCR pipeline. Not needed in case of a known work. pages: string|int, optional  None A specification of zero or more page numbers (see  fusus.lib.parseNums ). Only rows belonging to selected pages will be extracted. If None, all pages will be taken. load: boolean, optional  False If TF generation has succeeded, load the tf files for the first time. This will trigger a one-time precomputation step. loadOnly: boolean, optional  False Skip TF generation, assume the TF is already in place, and load it. This might trigger a one-time precomputation step. Returns    - nothing It will run the appripriate pipeline and generate tf in the appropriate locations.",
"func":1
},
{
"ref":"fusus.convert.makeTsv",
"url":5,
"doc":"Make TSV data out of the source of a work. The work is specified either by the name of a known work (e.g.  fususa ,  fususl ) or by specifying the work directory. The function needs to know whether the tsv comes out of an OCR process or from the text extraction of a PDF. In case of a known work, this is known and does not have to be specified. Otherwise you have to pass it. Parameters      source: string, optional  None The key of a known work, see  fusus.works.WORKS . Or the path to directory of the work. ocred: string Whether the tsv is made by the OCR pipeline. Not needed in case of a known work. pages: string|int, optional  None A specification of zero or more page numbers (see  fusus.lib.parseNums ). Only rows belonging to selected pages will be extracted. If None, all pages will be taken. Returns    - nothing It will run the appripriate pipeline and generate tsv in the appropriate locations.",
"func":1
},
{
"ref":"fusus.convert.loadTsv",
"url":5,
"doc":"Load a tsv file into memory. The tsv file either comes from a known work or is specified by a path. If it comes from a known work, you only have to pass the key of that work, e.g.  fususa , or  fususl . The function needs to know whether the tsv comes out of an OCR process or from the text extraction of a PDF. In case of a known work, this is known and does not have to be specified. Otherwise you have to pass it. Parameters      source: string, optional  None The key of a known work, see  fusus.works.WORKS . Or the path to the tsv file. ocred: string Whether the tsv file comes from the OCR pipeline. Not needed in case of a known work. pages: string|int, optional  None A specification of zero or more page numbers (see  fusus.lib.parseNums ). Only rows belonging to selected pages will be extracted. If None, all pages will be taken. Returns    - tuple Two members:  head: a tuple of field names  rows: a tuple of data rows, where each row is a tuple of its fields",
"func":1
},
{
"ref":"fusus.convert.parseArgs",
"url":5,
"doc":"Parse arguments from the command line. Performs sanity checks. Parameters      args: list All command line arguments. The full command is stripped from what  sys.argv yields. Returns    - passed: dict The interpreted values of the command line arguments, which will be passed on to the rest of program.",
"func":1
},
{
"ref":"fusus.convert.main",
"url":5,
"doc":"Perform tasks. See  HELP .",
"func":1
},
{
"ref":"fusus.works",
"url":6,
"doc":"Registry of sources. The  fusus package can work with source material in arbitrary locations. However, there is also a notion of  known works that  fusus has been designed for. This is the module where those works are registered. When new works become available, you can give them an acronym and register them here. See  WORKS . At this moment, all known works reside in this repo, under subdirectory  ur . It is easy to run pipeline commands on known works. Functions that deal with works can be given the acronym as an argument, and then they know how to deal with its data: Then you can do  sh python3 -m fusus.convert tsv acro   This will run the OCR pipeline and deliver TSV data as result;  -  sh python3 -m fusus.convert tf acro 7.3   This will convert the TSV data to TF and deliver the tf files in version 7.3  -  sh python3 -m fusus.convert tf acro 7.3 loadonly   This will load the TF data in version 7.3. The first time it loads, some extra computations will be performed, and a binary version of the tf files will be generated, which will be used for subsequent use by Text-Fabric.  - See also  fusus.convert ."
},
{
"ref":"fusus.works.BASE",
"url":6,
"doc":"Base directory for the data files. Currently this is the fusus repo itself. But it could be set to different places, if we want to separate the fusus code from the fusus data. You might consider to make it configurable, and pass it to the  fusus.book.Book and  fusus.lakhnawi.Lakhnawi objects."
},
{
"ref":"fusus.works.WORKS",
"url":6,
"doc":"Metadata of works in the pipeline. Here are the main works and the commentaries. They are given a keyword, and under that keyword are these fields:   meta metadata in the form of key value pairs that will be copied into Text-Fabric tf files;   source specification of   dir directory of the work,   file the TSV data file within that directory;   dest directory of the Text-Fabric data of this work;   toc whether the work has a table of contents; this is only relevant for the Lakhnawi edition, which has a table of contents that requires special processing. This processing is hard coded. So it will not work for other works with a table of contents.   ocred whether the work is the outcome of an OCR process; this is only false for the Lakhnawi edition, which is the result of a custom text extraction of a PDF. This text extraction is hard coded. So it will not work for other works that reside in a textual PDF.  ! hint \"fususa\" The Affifi page images are in the  in subdirectory of its work directory as specified in  WORKS .  ! caution \"fususl\" The Lakhnawi PDF does not reside in this repo. You have to obtain a copy by mailing to [Cornelis van Lit](mailto:l.w.c.vanlit@uu.nl) and place it in your repo clone as  _local/source/Lakhnawi/Lakhnawi.pdf .  ! hint \"commentaries\" Adding commentaries involves the following steps:  give a nice acronym to the commentary  add an entry in the source registry, keyed by that acronym  fill in the details  place the page image files in the  in subdirectory that you specified under  source and then  dir ."
},
{
"ref":"fusus.works.getWorkDir",
"url":6,
"doc":"Resolve a work location, given by key of directory. Parameters      source: string Key in the  WORKS dictionary ( known work) , or directory in the file system ( unknown work ). ocred: boolean or None Whether the work is in the OCR pipeline. For known works this is known, but it can be overriden. For unknown works it must be specified, and if not,  True is assumend. Returns    - (string | None, boolean | None) If the work is known and exists, or unknown and exists, its working directory is returned. If  givenOcr is  None , and the work is known, its ocr status is returned, otherwise None.",
"func":1
},
{
"ref":"fusus.works.getFile",
"url":6,
"doc":"Resolve a work data file location, given by key of directory. Parameters      source: string Key in the  WORKS dictionary ( known work) , or directory in the file system ( unknown work ). ocred: boolean or None Whether the work is in the OCR pipeline. For known works this is known, but it can be overriden. For unknown works it must be specified, and if not,  True is assumend. Returns    - (string | None, boolean | None) If the work is known and exists, or unknown and exists, its (tsv) data file is returned. If  givenOcr is  None , and the work is known, its ocr status is returned, otherwise None.",
"func":1
},
{
"ref":"fusus.works.getTfDest",
"url":6,
"doc":"Resolve a work tf directory, given by key of directory. Parameters      source: string Key in the  WORKS dictionary ( known work) , or directory in the file system ( unknown work ). versionTf: string The version of the TF data. This directory does not have to exist. Returns    - string | None If the work is known and exists, or unknown and exists, its versioned tf data directory is returned.",
"func":1
},
{
"ref":"fusus.lakhnawi",
"url":7,
"doc":"Lakhnawi pdf reverse engineering. This is an effort to make the Lakhnawi PDF readable. It is a text-based PDF, no images are used to represent text. Yet the text is not easily extracted, due to:  the use of private-use unicode characters that refer to heavily customised fonts;  some fonts have some glyphs with dual unicode points;  the drawing order of characters does not reflect the reading order;  horizontal whitespace is hard to detect due to oversized bounding boxes of many private-use characters. We used the top-notch Python PDF library [PyMUPDF](https: pymupdf.readthedocs.io/en/latest/index.html), also know as  fitz .   pip3 install PyMuPDF   But even this library could not solve the above issues. Here is how we solved the issues  Private use characters We used font analysis software from PdfLib: [FontReporter](https: www.pdflib.com/download/free-software/fontreporter/) to generate a [report of character and font usage in the Lakhnawi PDF](https: github.com/among/fusus/blob/master/ur/Lakhnawi/FontReport-Lakhnawi.pdf). Based on visual inspection of this font report and the occurrences of the private use tables we compiled a translation table mapping dirty strings (with private use characters) to clean strings (without private use characters).  Dual code points In case of dual code points, we ignore the highest code points. Often the two code points refer to a normal Arabic code point and to a ligature or special form of the character. The unicode algorithm is very good nowadays to generate the special forms from the ordinary forms based on immediate context.  Reading order We ordered the characters ourselves, based on the coordinates. This required considerable subtlety, because we had to deal with diacritics above and below the lines. See  clusterVert .  Horizontal whitespace This is the most tricky point, because the information we retain from the PDF is, strictly speaking, insufficient to determine word boundaries. Word boundaries are partly in the eyes of the beholder, if the beholder knows Arabic. The objective part is in the amount of whitespace between characters and the form of the characters (initial, final, isolated). But the rules of Arabic orthography allow initial characters inside words, and there are the enclitic words. So we only reached an approximate solution for this problem.  ! caution \"Footnotes\" We have strippped footnotes and footnote references from the text.  Output format The most important output are tab separated files with text and positions of individual words. See  Lakhnawi.tsvPages . This data is used to feed the conversion to Text-Fabric. See also:   fusus.tfFromTsv .  [Text-Fabric](https: annotation.github.io/text-fabric/tf/index.html)"
},
{
"ref":"fusus.lakhnawi.CSS",
"url":7,
"doc":"Styles to render extracted text. The styles are chosen such that the extracted text looks as similar as possible to the PDF display."
},
{
"ref":"fusus.lakhnawi.POST_HTML",
"url":7,
"doc":"HTML code postfixed to the HTML representation of a page."
},
{
"ref":"fusus.lakhnawi.preHtml",
"url":7,
"doc":"Generate HTML code to be prefixed to the HTML representation of a page. Parameters      pageNum: string The page number of the page for which HTML is generated.",
"func":1
},
{
"ref":"fusus.lakhnawi.getToc",
"url":7,
"doc":"Generate a Table Of Contents for multiple HTML pages. Parameter     - pageNums: iterable if int The page numbers of the pages in the HTML file.",
"func":1
},
{
"ref":"fusus.lakhnawi.REPLACE_DEF",
"url":7,
"doc":"Character replace rules There are two parts: (1) character replace rules (2) notes. Each rule consists of a left hand side, then  => , then a right hand side, then  : and then a short description. The short description may contain references to notes in the notes section, which is a list of commented lines at the end of the whole string. The left and right hand sides consist of one or more hexadecimal character codes, joined by the  + sign. The meaning is that when the left hand side matches a portion of the input text, the output text, which is otherwise a copy of the input text, will have that portion replaced by the right hand side. The exact application of rules has some subtleties which will be dealt with in  Laknawi.trimLine ."
},
{
"ref":"fusus.lakhnawi.ptRepD",
"url":7,
"doc":"Represent a float as an integer with enhanced precision. Parameters      p: float We multiply it by 10, then round it to the nearest integer. A none value is converted to  ? .",
"func":1
},
{
"ref":"fusus.lakhnawi.ptRep",
"url":7,
"doc":"Represent a float as an integer. Parameters      p: float We round it to the nearest integer. A none value is converted to  ? .",
"func":1
},
{
"ref":"fusus.lakhnawi.LETTER_CODE_DEF",
"url":7,
"doc":"Defines place holder  d in rule definitions."
},
{
"ref":"fusus.lakhnawi.getDictFromDef",
"url":7,
"doc":"Interpret a string as a dictionary. Parameters      defs: string A string containing definitions of character replace rules.  ! note \"Only for rules\" We only use this functions for the rules in  REPLACE_DEF .",
"func":1
},
{
"ref":"fusus.lakhnawi.FNRULE_WIDTH",
"url":7,
"doc":"Width of the rule that separates body text from footnote text."
},
{
"ref":"fusus.lakhnawi.SPACE_THRESHOLD",
"url":7,
"doc":"Amount of separation between words. Character boxes this far apart imply that there is a white space between them. The unit is 0.1 pixel."
},
{
"ref":"fusus.lakhnawi.Lakhnawi",
"url":7,
"doc":"Text extraction from the Lakhnawi PDF. This class makes use of the  fusus.char.UChar class which defines several categories of characters. By extending that class, the Lakhnawi class makes use of those categories. It also adds specific characters to some of those categories, especially the private use characters that occur in the Lakhnawi PDF. We use  fitz ( pip3 install PyMuPDF ) for PDF reading."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.close",
"url":7,
"doc":"Close the PDF handle, offered by  fitz .",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.setStyle",
"url":7,
"doc":"Import the CSS styles into the notebook. See  CSS .",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.getCharConfig",
"url":7,
"doc":"Configure all character information. Private-use characters, transformation rules, character categories.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.privateInfo",
"url":7,
"doc":"Set up additional character categories wrt. private-use characters. Several categories will receive additional members from the private use characters.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.setupRules",
"url":7,
"doc":"Set up character transformation rules. Prepare for counting how much rules will be applied when extracting text from pages of the Lakhnawi PDF.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.getCharInfo",
"url":7,
"doc":"Obtain detailed character information by reading the font report file. From this file we read:  which are the private use characters?  which of them have a double unicode? The font file is [here](https: github.com/among/fusus/blob/master/ur/Lakhnawi/FontReport-Lakhnawi.pdf).",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.plainChar",
"url":7,
"doc":"Show the character code of a character. Parameters      c: string The character in question, may also be the empty string or the integer 1 (diacritic place holder). Returns    - string The hexadecimal unicode point of  c , between  \u230a \u230b - brackets.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.plainString",
"url":7,
"doc":"Show the character codes of the characters in a string. Parameters      s: string The string to show, may be empty, may contain place holders. Returns    - string The concatenation of the unicode points of the characters in the string, each code point between brackets. See also  Lakhnawi.plainChar() .",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showChar",
"url":7,
"doc":"Pretty display of a single unicode character. We show the character itself and its name (if not a private-use one), its hexadecimal code, and we indicate by coloring the kind of white space that the character represents (ordinary space or tab). Parameters      c: string The character in question, may also be the empty string or the integer 1 (diacritic place holder).",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showString",
"url":7,
"doc":"Pretty display of a string as a series of unicode characters. Parameters      s: string The string to display, may be empty, may contain place holders. asString: boolean, optional  False If True, return the result as an HTML string. Returns    - None | string If  asString , returns an HTML string, otherwise returns None, but displays the HTML string. See also  Lakhnawi.showChar() .",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showReplacements",
"url":7,
"doc":"Show a character conversion rule and how it has been applied. Parameters      rule: string|int, optional  None A specification of zero or more rule numbers (see  fusus.lib.parseNums ). If None, all rules will be taken. isApplied: boolean, optional  False Only show rules that have been applied. Returns    - None Displays a table of rules with usage statistics.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showDoubles",
"url":7,
"doc":"Show a character with double entry and how often it occurs. See  Lakhnawi.doubles . Parameters      double: char, optional  None A character from the doubles list ( Lakhnawi.doubles ). If None, all such characters will be taken. isApplied: boolean, optional  False Only show rules that have been applied. Returns    - None Displays a table of double-entry characters with occurrence statistics.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showFinals",
"url":7,
"doc":"Show a character with final form and how often it has been replaced. Final forms will be normalized to ground forms and sometimes a space will be added. Parameters      final: char, optional  None A character from the final space list ( fusus.char.UChar.finalSpace ). If None, all such characters will be taken. isApplied: boolean, optional  False Only show rules that have been applied. Returns    - None Displays a table of final space characters with occurrence statistics.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showLineHeights",
"url":7,
"doc":"Shows how line heights have been determined. The pages can be selected by page numbers. Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() .",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.parsePageNums",
"url":7,
"doc":"Parses a value as one or more page numbers. Parameters      pageNumSpec: None | int | string | iterable If  None results in all page numbers. If an  int , it stands for that int. If a  string , it is allowed to be a comma separated list of numbers or ranges, where a range is a lower bound and an upper bound separated by a  - . If none of these, it should be an iterable of  int values. Returns    - None | iterable of int Depending on the value.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.drawPages",
"url":7,
"doc":"Draws a (part) of page from the PDF as a raster image. Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . clip: (int, int), optional  None If None: produces the whole page. Otherwise it is  (top, bottom) , and a stripe from top to bottom will be displayed.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.getPages",
"url":7,
"doc":"Reads pages of the PDF and extracts text. This does all of the hard work of the text extraction. It saves the textual data in attributes of the Lakhnawi object, augmented with all kinds of diagnostic information. From all this data, various output representations can be generated rather easily by other methods. Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . refreshConfig: boolean, optional  False If  True , rereads all character configuration. Ideal when you are iteratively developing the character configuration. doRules: boolean, optional  True If  False , suppresses the application of character transformation rules. Mainly used when debugging other aspects of the text extraction. doFilter: boolean, optional  True If  False , suppresses the application of unicode normalization, by which presentational characters are transformed into sequences of ordinary, basic characters. Used for debugging. onlyFnRules: boolean, optional  False If  True , skips most of the conversion. Only determine where the footnote rules are. Used for debugging. Returns    - None The effect is that attributes of the Lakhnawi object are filled:   Lakhnawi.heights   Lakhnawi.clusteredHeights   Lakhnawi.fnRules For the other attributes, see  Lakhnawi.collectPage() .  ! hint \"multiple runs\" If you do multiple runs of this function for different pages, the results will not overwrite each other in general, because the attributes hold the results in dictionaries keyed by page number.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.getPageRaw",
"url":7,
"doc":"Do a rough/raw text extract of a specific page. The  fitz method [extractRAWDICT()](https: pymupdf.readthedocs.io/en/latest/textpage.html TextPage.extractRAWDICT) is used to obtain very detailed information about each character on that page. Used for debugging. Parameters      pageNum: int A valid page number. It is the sequence number of the page within the PDF, counting from 1. Returns    - None It pretty prints the output of the fitz method, which is a big and deep dictionary.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.getPageObj",
"url":7,
"doc":"Get the  fitz object for a specific page. Used for debugging. Parameters      pageNum: int A valid page number. It is the sequence number of the page within the PDF, counting from 1. Returns    - object A  fitz [page object](https: pymupdf.readthedocs.io/en/latest/page.html)",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.plainPages",
"url":7,
"doc":"Outputs processed pages as plain text. Uses  Lakhnawi.plainLine() . Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . Returns    - None The plain text is printed to the output.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.tsvPages",
"url":7,
"doc":"Outputs processed pages as tab-separated data. Uses  Lakhnawi.tsvLine() . and  Lakhnawi.tsvHeadLine() . Here is the structure: Each page is divided into lines. Each line is divided into columns (in case of hemistic verses, see  Lakhnawi.columns ). Each column is divided into spans. Span transitions occur precisely there where changes in writing direction occur. Each span is divided into words. Each word occupies exactly one line in the TSV file, with the following fields:   page page number   line line number within the page   column column number within the line   span span number within the column   direction ( l or  r ) writing direction of the span   left  x coordinate of left boundary   top  y coordinate of top boundary   right  x coordinate of right boundary   bottom  y coordinate of bottom boundary   text text of the word Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . Returns    - None The tab-separated data is written to a single tsv file. There is a heading row. The file is in  fusus.parameters.UR_DIR , under  Lakhnawi . The name of the file includes a page specification.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.htmlPages",
"url":7,
"doc":"Outputs processed pages as formatted HTML pages. Uses  Lakhnawi.htmlLine() . The HTML output is suitable to read the extracted text. Its layout matches the original closely, which makes it easier to see where the output deviates from the source page. Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . line: None | int | string | iterable A specification of zero or more line numbers (see  fusus.lib.parseNums ). showSpaces: boolean, optional  False If  True , shows the spaces with a conspicuous coloured background. export: boolean, optional  False If  True , writes the HTML results to disk. In this case, the HTML will not be displayed in the notebook. singleFile: boolean, optional  False Only meaningful is  export=True . If  True , writes the output to a single HTML file, otherwise to one file per page, in a directory called  html . toc: boolean, optional  False Only meaningful is  export=True and  singleFile=True . If  True , writes a table of contents to the file. The TOC points to every page that is included in the output file. Returns    - None Depending on  export , the page is displayed in the notebook where this function is called, or exported to a file on disk. The file is in  fusus.parameters.UR_DIR , under  Lakhnawi . The name of the file includes a page specification.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showLines",
"url":7,
"doc":"Outputs processed lines as a formatted HTML table. The lines can be selected by page numbers and line numbers. Within the selected lines, the characters can be selected by start/end postions, or by characters of interest. All of these indices start at 1. Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . line: None | int | string | iterable A specification of zero or more line numbers (see  fusus.lib.parseNums ). start: integer, optional  None Starting word position in each line to be output. If  None , starts at the beginning of each line. end: integer, optional  None End word position in each line to be output. If  None , ends at the end of each line. search: string or iterable of char, optional  None If not none, all characters in  search are deemed interesting. All occurrences of these characters within the selected lines are displayed, included a small context. orig: boolean, optional  False Only meaningful if  search is given. If  True : the check for interesting characters is done in the original, untranslated characters. Otherwise, interesting characters are looked up in the translated characters. every: boolean, optional  False Only meaningful if  search is given. If  True , when looking for interesting characters, all occurrences will be retrieved, otherwise only the first one. Returns    - None The output material will be displayed in the notebook.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showWords",
"url":7,
"doc":"Outputs processed words as a formatted HTML table. The lines can be selected by page numbers and line numbers. All words within the selected lines are put into a table with the same properties as in the TSV data, see  Lakhnawi.tsvPages . Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . line: None | int | string | iterable A specification of zero or more line numbers (see  fusus.lib.parseNums ). Returns    - None The output material will be displayed in the notebook.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showUsedChars",
"url":7,
"doc":"Show used characters. Gives an overview of character usage, either in the input PDF, or in the text output. Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . orig: boolean, optional  False If  True : shows characters of the original PDF. Otherwise, shows characters of the translated output/ onlyPuas: boolean, optional  False If  True , the result is restricted to private use characters. onlyPresentational: boolean, optional  False If  True , the result is restricted to presentational characters. See  fusus.char.UChar.presentational . long: boolean, optional  False If  True , for each character output the complete list of pages where the character occurs. Otherwise, show only the most prominent pages. byOcc: boolean, optional  False If  True , sort the results by first occurrence of the characters. Otherwise, sort the results by unicode code point of the character. Returns    - None The output material will be displayed in the notebook.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showColumns",
"url":7,
"doc":"Show used characters. Gives an overview of the columns in each line. The result is a readable, ascii overview of the columns that exists in the lines of the selected pages. It is useful to visually check column detection for many pages. Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . Returns    - None The output material will be displayed in the notebook.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.showSpacing",
"url":7,
"doc":"Show where the spaces are. Gives an overview of the white space positions in each line. It is useful to debug the horizontal white space algorithm. Parameters      pageNumSpec: None | int | string | iterable As in  Lakhnawi.parsePageNums() . line: None | int | string | iterable A specification of zero or more line numbers (see  fusus.lib.parseNums ). Returns    - None The output material will be displayed in the notebook.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.collectPage",
"url":7,
"doc":"Transforms raw text into proper textual data. Called by  Lakhnawi.getPages() and delivers its results to attributes of the Lakhnawi object. Here are they   Lakhnawi.lines   Lakhnawi.doubles   Lakhnawi.text They are all dictionaries, keyed by page number first and then by line. Parameters      data: dict as obtained by the [extractRAWDICT()](https: pymupdf.readthedocs.io/en/latest/textpage.html TextPage.extractRAWDICT) method of  fitz . Returns    - None",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.isPageNum",
"url":7,
"doc":"Checks whether a series of characters represents an arabic number. Parameters      chars: iterable of char reocrds",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.trimLine",
"url":7,
"doc":"Map character sequences to other sequences. Two tasks: 1. Map private use characters to well-known unicode characters 2. Insert space characters where the next character is separated from the previous one. Complications: Diacritical characters are mostly contained in a very wide box that overlaps with the boxes of the other characters. So the diacritical boxes must not be taken into account. Private use characters often come in sequences, so a sequence of characters must be transformed to another sequence. We do the tramsformation before the space insertion, because otherwise we might insert the space at the wrong point. When we transform characters we need to retain the box information, because we still have to insert the space. That's why we have as input a list of character records, where each record is itself a list with box information, orginal character, modified characters and space information. When we transform characters, we modify character records in place. We do not add or remove character records. The last member of a character record is the modified sequence. This can be zero, one, or multiple characters. The second last member is the original character. Initially, the the last and second last member of each record are equal. We call these members the original character and the result string. Space will be appended at the last member of the appropriate character records. The transformations are given as a set of rules. See  REPLACE_DEFS . A rule consists of a sequence of characters to match and a sequence of characters to replace the match with. We call them the match sequence and the replacement sequence of the rule. For each character in the input list we check which rules have a match sequence that start with this character. Of these rules, we start with the one with the longest match sequence. We then check, by looking ahead, whether the whole match sequence matches the input. For the purposes of matching, we look into the result strings of the character, not to the original characters. This will prevent some rules to be applied after an earlier rule has been applied. This is intentional, and results in a more simple rule set. If there is a match, we walk through all the characters in the input for the length of the match sequence of the rule. For each input character record, we set its replacement string to the corresponding member of the replacement sequence of the rule. If the replacement sequence has run out, we replace with the empty string. If after this process the replacement sequence has not been exhausted, we join the remaining characters in the replacement string and append it after the replacement string of the last input character that we have visited. After succesful application of a rule, we do not apply other rules that would have been applicable at this point. Instead, we move our starting point to the next character record in the sequence and repeat the matching process. It might be that a character is replaced multiple times, for example when it is reached by a rule while looking ahead 3 places, and then later by a different rule looking ahead two places. However, once a character matches the first member of the match sequence of a rule, and the rule matches and is applied, that character will not be changed anymore by any other rule.  ! caution \"place holders for diacritics\" The following functionality exists in the code, but is not needed anymore to process the Lakhnawi PDF. The match sequence may contain the character  d , which is a placeholder for a diacritic sign. It will match any diacritic. The replacement sequence of such a rule may or may not contain a  d . It is an error if the replacement seqience of a rule contains a  d while its match sequence does not. It is also an error of there are multiple  d s in a match sequence of a replacement sequence. If so, the working of this rule is effectively two rules: Suppose the rule is x d y => r d s where x, y, r, s are sequences of arbitrary length. If the rule matches the input, then first the rule x => r will be applied at the current position. Then we shift temporarily to the position right after where the d has matched, and apply the rule y => s Then we shift back to the orginal position plus one, and continue applying rules.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.plainLine",
"url":7,
"doc":"Outputs a processed line as plain text. Used by  Lakhnawi.plainPages() . Parameters      columns: iterable An iterable of columns that make up a line. Each column is an iterable of spans. Spans contain words plus an indication of the writing direction for that span. Returns    - string The concatenation of all words in all spans separated by white space.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.tsvHeadLine",
"url":7,
"doc":"Outputs the field names of a word in TSV data. See  Lakhnawi.tsvPages() for the structure of TSV data as output format for the extracted text of the Lakhnawi PDF. Returns    - string A tab-separated line of field names.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.tsvLine",
"url":7,
"doc":"Outputs a processed line as lines of tab-separated fields for each word. Used by  Lakhnawi.tsvPages() . Parameters      columns: iterable An iterable of columns that make up a line. Each column is an iterable of spans. Spans contain words plus an indication of the writing direction for that span. pageNum: int The page number of the page where this line occurs. Returns    - string The concatenation of the TSV lines for all words in all spans in all columns.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.htmlLine",
"url":7,
"doc":"Outputs a processed line as HTML. Used by  Lakhnawi.htmlPages() . Parameters      columns: iterable An iterable of columns that make up a line. Each column is an iterable of spans. Spans contain words plus an indication of the writing direction for that span. prevMulti: boolean Whether the preceding line has multiple columns. isLast: boolean Whether this line is the last line on the page. Returns    - string The concatenation of the TSV lines for all words in all spans in all columns.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.clusterVert",
"url":7,
"doc":"Cluster characters into lines based on their bounding boxes. Most characters on a line have their middle line in approximately the same height. But diacritics of characters in that line may occupy different heights. Without intervention, these would be clustered on separate lines. We take care to cluster them into the same lines as their main characters. It involves getting an idea of the regular line height, and clustering boxes that fall between the lines with the line above or below, whichever is closest. The result of the clustering is delivered as a key function, which will be used to sort characters. Parameters      data: iterable of record The character records Returns    - function A key function that assigns to each character record a value that corresponds to the vertical position of a real line, which is a clustered set of characters. The information on the vertical clustering of lines is delivered in the attributes  Lakhnawi.heights and  Lakhnawi.clusteredHeights , on a page by page basis.",
"func":1
},
{
"ref":"fusus.lakhnawi.Lakhnawi.heights",
"url":7,
"doc":"Heights of characters, indexed by page number."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.clusteredHeights",
"url":7,
"doc":"Clustered heights of characters, indexed by page number. The clustered heights correspond to the lines on a page."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.lines",
"url":7,
"doc":"Lines as tuples of original character objects, indexed by page number"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.text",
"url":7,
"doc":"Lines as tuples of converted character objects, indexed by page number"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.fnRules",
"url":7,
"doc":"Vertical positions of footnote lines, indexed by page number"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.spaces",
"url":7,
"doc":"Spacing information for each character, indexed by page and line number. For character that has space behind it, it gives the index position of that character in the line, the amount of space detected, and whether this counts as a full white space."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.columns",
"url":7,
"doc":"Column information, indexed by page and line number. Spaces that are significantly larger than a normal white space are interpreted as a tab, and these are considered as column separators. We remember the character positions where this happens plus the amount of space in question. Columns in the Lakhnawi PDF correspond to  hemistic poems, where lines are divided into two halves, each occupying a column. See ![hemistic](images/hemistic.png)  ! caution \"hemistic poems versus blocks\" This is very different from blocks (see  fusus.layout ) in OCRed texts, where blocks have been detected because of vertical strokes that separate columns. The reading progress in a hemistic poem is not changed by the column division, where as in the case of blocks, reading proceeds by reading the complete blocks in order."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.doubles",
"url":7,
"doc":"Glyphs with double unicode points. Some private use characters have two unicode points assigned to them by fonts in the PDF. This is the cause that straightforward text extractions deliver double occurrences of those letters. Even  fitz does that. We have collected these cases, and choose to use the lower unicode point, which is usually an ordinary character, whereas the other is usually a related presentational character. This dictionary maps the lower character to the higher character."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.privateLetters",
"url":7,
"doc":"Private-use unicodes that correspond to full letters."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.privateDias",
"url":7,
"doc":"Private-use unicodes that correspond to diacritics."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.privateSpace",
"url":7,
"doc":"Private-use-unicode used to represent a space."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.good",
"url":7,
"doc":"Whether processing is still ok, i.e. no errors encountered."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.puas",
"url":8,
"doc":"Private use character codes as defined by the unicode standard."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.arabic",
"url":8,
"doc":"All Arabic unicode characters"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.hebrew",
"url":8,
"doc":"All Hebrew unicode characters"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.syriac",
"url":8,
"doc":"All Syriac unicode characters"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.latinPresentational",
"url":8,
"doc":"Ligatures and special letter forms in the Latin script"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.greekPresentational",
"url":8,
"doc":"Ligatures and special letter forms in the Greek script"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.arabicPresentational",
"url":8,
"doc":"Ligatures and special letter forms in the Arabic script"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.hebrewPresentational",
"url":8,
"doc":"Ligatures and special letter forms in the Hebrew script"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.presentationalC",
"url":8,
"doc":"Ligatures and special letter forms (C) These are the ones that are best normalized with  NFKC : Arabic and Hebrew."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.presentationalD",
"url":8,
"doc":"Ligatures and special letter forms (D) These are the ones that are best normalized with  NFKD : Latin and Greek."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.presentational",
"url":8,
"doc":"Ligatures and special letter forms various scripts"
},
{
"ref":"fusus.lakhnawi.Lakhnawi.stops",
"url":8,
"doc":"Characters that have the function of a full stop in several scripts."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.punct",
"url":8,
"doc":"Punctuation characters in several scripts."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.semis",
"url":8,
"doc":"Characters in semitic scripts. These scripts have a right-to-left writing direction."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.rls",
"url":8,
"doc":"Characters that belong to the right-to-left writing direction. Identical with the  UChar.semis category. But the Lakhnawi conversion will insert the private use characters to this category."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.bracketMap",
"url":8,
"doc":"Mapping between left and right versions of brackets. Due to Unicode algorithms, left and right brackets will be displayed flipped when used in right-to-left writing direction.  ! caution \"hard flipping\" The Lakhnawi PDF contains brackets that have been hard flipped in order to display correctly in rtl direction. But after text extraction, we can rely on the Unicode algorithm, so we have to unflip these characters."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.nonLetter",
"url":8,
"doc":"Characters that act as symbols. More precisely, these are the non letters that we may encounter in  Arabic script, including symbols from other scripts and brackets."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.neutrals",
"url":8,
"doc":"Characters that are neutral with respect to writing direction. These are the characters that should not trigger a change in writing direction. For example, a latin full stop amidst Arabic characters should not trigger a character range consisting of that full stop with ltr writing direction."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.nospacings",
"url":8,
"doc":"Characters that will be ignored when figuring out horizontal white space. These are characters that appear to have bounding boxes in the Lakhnawi PDF that are not helpful in determining horizontal white space. When using this category in the Lakhnawi text extraction, extra characters will be added to this category, namely the diacritics in the private use area. But this is dependent on the Lakhnawi PDF and the Lakhnawi text extraction will take care of this."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.diacritics",
"url":8,
"doc":"Diacritical characters in various scripts."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.diacriticLike",
"url":8,
"doc":"Diacritical characters in various scripts plus the Arabic Hamza 0621."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.arabicLetters",
"url":8,
"doc":"Arabic characters with exception of the Arabic diacritics."
},
{
"ref":"fusus.lakhnawi.Lakhnawi.finalSpace",
"url":8,
"doc":"Space insertion triggered by final characters. Some characters imply a word-boundary after them. Characters marked as \"FINAL\" by Unicode are candidates, but not all of them have this behaviour. Here is the exact set of characters after which we need to trigger a word boundary."
},
{
"ref":"fusus.lakhnawi.keyCharV",
"url":7,
"doc":"The vertical position of the middle of a character. Used to sort the characters of a page in the vertical direction. Parameters      char: record Returns    - float The height of the middle of the character.",
"func":1
},
{
"ref":"fusus.lakhnawi.keyCharH",
"url":7,
"doc":"Sort key to sort the characters of a line horizontally. Basically, characters whose right edge are closer to the right edge of the page come before characters whose right edges are further left. So we could sort on minus the x coordinate of the right edge. However, there are complications. Sometimes characters have the same right edge. Diacritics usually start right after the letter they are on together with the next letter. So they should come before that next letter. In those cases we take the width into account. Private use diacritics usually have a big width, they are wider than letters. So if we sort wider characters before narrower characters, we get that right. However, normal unicode diacritics have a typical width of zero, and also these should come before the next letter. We can solve that by sorting by a key defined as 1 divided by the width if the width is nonzero, and 0 if the the width is zero. Then zero width characters come first, then wide characters, then narrow characters. One extra complication: the widths are not integers but fractions. Sometimes a the diacritic and the next letter have an almost equal right edge, but not quite equal, and the wrong one comes first. We can solve that by rounding. Parameters      char: record Returns    - (int, float)",
"func":1
},
{
"ref":"fusus.char",
"url":8,
"doc":"Character knowledge. This module collects all character knowledge that we need to parse the Lakhnawi PDF and makes it available to programs. It contains definitions for things as character classes, e.g.  symbols ,  presentational characters ,  punctuation ,  bracket-like characters , etc. See  UChar below."
},
{
"ref":"fusus.char.uName",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.getSetFromCodes",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.getSetFromRanges",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.getSetFromDef",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.getMapFromPairs",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.normalizeC",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.normalizeD",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.isAlefFinal",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.isMeemOrYeh",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.isWaw",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.isArDigit",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.isEuDigit",
"url":8,
"doc":"",
"func":1
},
{
"ref":"fusus.char.UChar",
"url":8,
"doc":""
},
{
"ref":"fusus.char.UChar.puas",
"url":8,
"doc":"Private use character codes as defined by the unicode standard."
},
{
"ref":"fusus.char.UChar.arabic",
"url":8,
"doc":"All Arabic unicode characters"
},
{
"ref":"fusus.char.UChar.hebrew",
"url":8,
"doc":"All Hebrew unicode characters"
},
{
"ref":"fusus.char.UChar.syriac",
"url":8,
"doc":"All Syriac unicode characters"
},
{
"ref":"fusus.char.UChar.latinPresentational",
"url":8,
"doc":"Ligatures and special letter forms in the Latin script"
},
{
"ref":"fusus.char.UChar.greekPresentational",
"url":8,
"doc":"Ligatures and special letter forms in the Greek script"
},
{
"ref":"fusus.char.UChar.arabicPresentational",
"url":8,
"doc":"Ligatures and special letter forms in the Arabic script"
},
{
"ref":"fusus.char.UChar.hebrewPresentational",
"url":8,
"doc":"Ligatures and special letter forms in the Hebrew script"
},
{
"ref":"fusus.char.UChar.presentationalC",
"url":8,
"doc":"Ligatures and special letter forms (C) These are the ones that are best normalized with  NFKC : Arabic and Hebrew."
},
{
"ref":"fusus.char.UChar.presentationalD",
"url":8,
"doc":"Ligatures and special letter forms (D) These are the ones that are best normalized with  NFKD : Latin and Greek."
},
{
"ref":"fusus.char.UChar.presentational",
"url":8,
"doc":"Ligatures and special letter forms various scripts"
},
{
"ref":"fusus.char.UChar.stops",
"url":8,
"doc":"Characters that have the function of a full stop in several scripts."
},
{
"ref":"fusus.char.UChar.punct",
"url":8,
"doc":"Punctuation characters in several scripts."
},
{
"ref":"fusus.char.UChar.semis",
"url":8,
"doc":"Characters in semitic scripts. These scripts have a right-to-left writing direction."
},
{
"ref":"fusus.char.UChar.rls",
"url":8,
"doc":"Characters that belong to the right-to-left writing direction. Identical with the  UChar.semis category. But the Lakhnawi conversion will insert the private use characters to this category."
},
{
"ref":"fusus.char.UChar.bracketMap",
"url":8,
"doc":"Mapping between left and right versions of brackets. Due to Unicode algorithms, left and right brackets will be displayed flipped when used in right-to-left writing direction.  ! caution \"hard flipping\" The Lakhnawi PDF contains brackets that have been hard flipped in order to display correctly in rtl direction. But after text extraction, we can rely on the Unicode algorithm, so we have to unflip these characters."
},
{
"ref":"fusus.char.UChar.nonLetter",
"url":8,
"doc":"Characters that act as symbols. More precisely, these are the non letters that we may encounter in  Arabic script, including symbols from other scripts and brackets."
},
{
"ref":"fusus.char.UChar.neutrals",
"url":8,
"doc":"Characters that are neutral with respect to writing direction. These are the characters that should not trigger a change in writing direction. For example, a latin full stop amidst Arabic characters should not trigger a character range consisting of that full stop with ltr writing direction."
},
{
"ref":"fusus.char.UChar.nospacings",
"url":8,
"doc":"Characters that will be ignored when figuring out horizontal white space. These are characters that appear to have bounding boxes in the Lakhnawi PDF that are not helpful in determining horizontal white space. When using this category in the Lakhnawi text extraction, extra characters will be added to this category, namely the diacritics in the private use area. But this is dependent on the Lakhnawi PDF and the Lakhnawi text extraction will take care of this."
},
{
"ref":"fusus.char.UChar.diacritics",
"url":8,
"doc":"Diacritical characters in various scripts."
},
{
"ref":"fusus.char.UChar.diacriticLike",
"url":8,
"doc":"Diacritical characters in various scripts plus the Arabic Hamza 0621."
},
{
"ref":"fusus.char.UChar.arabicLetters",
"url":8,
"doc":"Arabic characters with exception of the Arabic diacritics."
},
{
"ref":"fusus.char.UChar.finalSpace",
"url":8,
"doc":"Space insertion triggered by final characters. Some characters imply a word-boundary after them. Characters marked as \"FINAL\" by Unicode are candidates, but not all of them have this behaviour. Here is the exact set of characters after which we need to trigger a word boundary."
},
{
"ref":"fusus.page",
"url":9,
"doc":"Single page processing."
},
{
"ref":"fusus.page.Page",
"url":9,
"doc":"All processing steps for a single page. Parameters      engine: object The  fusus.book.Book object f: string The file name of the scanned page with extension, without directory sizeW: float, default 1 If the image is a fraction of a page, this is the fraction of the width sizeH: float, default 1 If the image is a fraction of a page, this is the fraction of the size minimal: boolean, optional  False If true, do not read image files, just initialize data structures batch: boolean, optional  False Whether to run in batch mode. In batch mode everything is geared to the final output. Less intermediate results are computed and stored. Less feedback happens on the console. boxed: boolean, optional  True If in batch mode, produce also images that display the cleaned marks in boxes."
},
{
"ref":"fusus.page.Page.show",
"url":9,
"doc":"Displays processing stages of an page. See  fusus.parameters.STAGES . Parameters      stage: string | iterable, optional  None If no stage is passed, all stages are shown as thumbnails. Otherwise, the indicated stages are shown. If a string, it may be a comma-separated list of stage names. Otherwise it is an iterable of stage names. band: string | iterable, optional  None If no band is passed, no bands are indicated. Otherwise, the indicated bands are shown. If a string, it may be a comma-separated list of band names. Otherwise it is an iterable of band names. mark: string | iterable, optional  None If  None is passed, no marks are shown. If    is passed, all marks on the selected bands are shown. Otherwise, the indicated mark boxes are shown, irrespective of their bands: If given as a string, it may be a comma-separated list of mark names. Otherwise it is an iterable of mark names. This information will be taken from the result of the  markData stage. display: dict, optional A set of display parameters, such as  width ,  height (anything accepted by  IPython.display.Image ). Notes   - The mark option works for the \"boxed\" stage: All marks not specified in the mark parameter will not be shown. But this option also works for all other image stages: the marks will be displayed on a fresh copy of that stage. When used for a grayscale stage, the color of the mark boxes is lost.",
"func":1
},
{
"ref":"fusus.page.Page.stagePath",
"url":9,
"doc":"",
"func":1
},
{
"ref":"fusus.page.Page.read",
"url":9,
"doc":"Reads processing data for selected stages from disk Parameters      stage: string | iterable, optional  None If no stage is passed, all stages will be read, if corresponding files are present. Otherwise, the indicated stages are read.",
"func":1
},
{
"ref":"fusus.page.Page.write",
"url":9,
"doc":"Writes processing stages of an page to disk. Parameters      stage: string | iterable, optional  None If no stage is passed, all stages are shown as thumbnails. Otherwise, the indicated stages are shown. If a string, it may be a comma-separated list of stage names. Otherwise it is an iterable of stage names. perBlock: boolean, optional  False If True, the stage output will be split into blocks and written to disk separately. The stripe and column of a block are appended to the file name. Returns    - None The stages are written into the  inter or  clean subdirectory, with the name of the stage appended to the file name. If  clean , the name of the stage is omitted.",
"func":1
},
{
"ref":"fusus.page.Page.doNormalize",
"url":9,
"doc":"Normalizes a page. Previously needed to unskew pages. But now we assume pages are already skewed. Skewing turned out to be risky: when pages are filled in unusual ways, we got unexpected and unwanted rotations. So we don't do that anymore. If the input page images have skew artefacts (black sharp triangles in the corners) as a result of previous skewing these will be removed. Normalization produces the stages:   gray : grayscale version of  orig   blurred : inverted, black-white, blurred without skew artefacts, needed for histograms later on;   normalized :  gray without skew artefacts;   normalizedC :  orig without skew artefacts.",
"func":1
},
{
"ref":"fusus.page.Page.doLayout",
"url":9,
"doc":"Divide the page into stripes and the stripes into columns. We detect vertical strokes as columns separators and horizontal strokes as separators to split off top and bottom material. A page may or may not be partially divided into columns. Where there is a vertical stroke, we define a stripe: the horizontal band that contains the vertical stroke tightly and extends to the full with of the page. Between the stripes corresponding to column separators we have stripes that are not split into columns. The stripes will be numbered from top to bottom, starting at 1. If a stripe is not split, it defines a roi (region of interest) with label  (i,  ) . If it is split, it defines blocks with labels  (i, 'r') and  (i, 'l') . Every horizontal stripe will be examined. We have to determine whether it is a top separator or a bottom separator. As a rule of thumb: horizontal stripes in the top stripe are top-separators, all other horizontal stripes are bottom separators. If there are multiple horizontal strokes in a roi, the most aggressive one will be taken, i.e. the one that causes the most matarial to be discarded. All further operations will take place on these blocks (and not on the page as a whole). The result of this stage is, besides the blocks, an image of the page with the blocks marked and labelled.",
"func":1
},
{
"ref":"fusus.page.Page.cleaning",
"url":9,
"doc":"Remove marks from the page. The blocks of the page are cleaned of marks. New stages of the page are added:   clean all targeted marks removed   cleanh all targeted marks highlighted in light gray   boxed all targeted marks boxed in light gray   markData information about each detected mark. Parameters      mark: iterable of tuples (band, mark, [params]), optional  None If  None , all marks that are presented in the book directory are used. Otherwise, a series of marks is specified together with the band where this mark is searched in. Optionally you can also put parameters in the tuple: the accuracy, connectBorder and connectRatio. block: (integer, string), optional  None Block identifier. If specified, only this block will be cleaned. If absent, cleans all blocks. line: integer, optional  None Line number specifying the line numbers to clean. In all specified blocks, only the line with this number will be cleaned. If absent, cleans all lines in the specified blocks. showKept: boolean, optional  False Whether to show the mark candidates that are kept. If False, kept marks do not show up as green boxes, and they do not contribute to the markData layer.",
"func":1
},
{
"ref":"fusus.page.Page.ocring",
"url":9,
"doc":"Calls the OCR engine for a page.",
"func":1
},
{
"ref":"fusus.page.Page.proofing",
"url":9,
"doc":"Produces proofing images",
"func":1
},
{
"ref":"fusus.pdf",
"url":10,
"doc":""
},
{
"ref":"fusus.pdf.pdf2png",
"url":10,
"doc":"Extract all images in a PDF to an output directory.",
"func":1
},
{
"ref":"fusus.about",
"url":11,
"doc":" Documents Higher level documentation."
},
{
"ref":"fusus.about.model",
"url":12,
"doc":" OCR Models for Kraken Here are the models we use for doing OCR with [Kraken](https: github.com/mittagessen/kraken):  Arabic Generaized Model from [OpenITI](https: github.com/OpenITI/OCR_GS_Data). The file we are using is this one exactly (the commit is specified): [OCR_GS_Data/ara/abhath/arabic_generalized.mlmodel](https: github.com/OpenITI/OCR_GS_Data/blob/1e41e57f1e3c36b40d439f87ad0685d2c2316099/ara/abhath/arabic_generalized.mlmodel)"
},
{
"ref":"fusus.about.sources",
"url":13,
"doc":" Availability Some sources are not publicly available in this repository. They are in the directory _local_, which is excluded from git tracking. These files might be available upon request to [Cornelis van Lit](https: digitalorientalist.com/about-cornelis-van-lit/). All results obtained from these source materials are publicly available.  ! caution \"No editorial material\" We have taken care to strip all editorial material from the sources. We only process the original, historical portions of the texts.  ! hint \"Intermediate results are reproducible\" This repository may or may not contain intermediate results, such as proofing pages, cleaned images, pages with histograms. By running the pipeline again, these results can be reproduced, even without recourse to the original materials in the  _local directory.  Fusus Al Hikam The seminal work is the Fusus Al Hikam (Bezels of Wisdom) by [Ibn Arabi 1165-1240](https: en.wikipedia.org/wiki/Ibn_Arabi). We use two editions, by Lakhnawi and by Affifi.  Lakhnawi edition Cornelis obtained by private means a pdf with the typeset text in it. The text cannot be extracted by normal means due to a range of problems, among with the unusual encoding of Arabic characters to drive special purpose fonts. We have reversed engineered the pdf and produced versions in tsv files, plain text, html, Text-Fabric as well as raster images. The pdf that we worked from is not in the repository, but the results are in the  ur/Lakhnawi directory. The Text-Fabric result is in the  tf/fusus/Lakhnawi directory, where versioned releases of the tf data reside.  Affifi edition Cornelis obtained a pdf with the text as page images in it. We have used the fusus pipeline to extract the full text involving OCR. The pdf that we worked from is not in the repository, but the results are in the  ur/Affifi directory.  Commentaries Cornelis has prepared page images for several commentaries, which we have carried through the fusus pipeline. The results are in the  ur/xxx directories, where  xxx stands for the acronym of the commentary."
},
{
"ref":"fusus.about.install",
"url":14,
"doc":" Convention A lot of configuration can be avoided by this simple convention: Put your cloned version of this repository in your  ~/github directory. If you do not have it, make it, and organize it exactly as GitHub is organized: by organization and then by repo.  Get the software Clone the  among/fusus repo from GitHub. Here are the instructions to get this repo and place it in the conventional place on your file system.  sh cd mkdir github cd github mkdir among git clone https: github.com/among/fusus cd fusus   If you want to update later, make sure that you do not have work of your own in this repo. If you have, copy it to a location outside of this repo.  sh cd ~/github/among/fusus git fetch origin git checkout master git reset  hard origin/master    Install the software You are going to install the Python package  fusus that is contained in the repo. We install fusus  fusus with  pip3 from the clone, not from the global, online PyPI repository. During install, all the packages that  fusus is dependent on, will be installed into your current Python3 installation. The package  fusus itself will be added to your Python3 installation in such a way that it can be used from anywhere, while the package inside the repo is being accessed. This is achieved by the fact that the installer will create a link to the repo.  sh cd ~/github/among/fusus pip3 install -e .    ! caution \"Mind the dot\" Do not forget the  . at the end of the line in the above instruction.  ! hint \"No nead to repeat this step\" When you update the repo later, it will not be necessary to redo the  pip3 install step, because the soft link to the fusus package in the repo will still be valid.  Build steps The following steps are relevant if you modify the software and documentation. There is a script  build.py in the top-level directory that performs these tasks. Go to the repo's top level directory and say  sh python3 build.py  help   to see what it can do. Tip: in your  .zshrc define this function:  sh function fsb { cd ~/github/among/fusus python3 build.py \"$@\" }   Then you can invoke the build script from anywhere:  sh fsb  help    Documentation The docs are here:  the README file of the repository;  the docstrings in the Python files in the  fusus package;  the markdown files in the  docs subdirectory of the  fusus package. Edit the sources of documentation in your local repo clone and use a set of build commands to display and publish the modified docs.  View documentation locally To open a browser and view the dynamically generated documentation, say  sh fsb docs    ! caution \"Limited functionality\" The search function does not work here, and images will not display. This way of local browsing the docs has the advantage that changes in the docs are detected when you save them, so that you can see the effect immediately.  Generate documentation locally To generate documentation, say  sh fsb pdocs   The documentation is now in the  site directory. Go to the  index.html file there and open it in your browser. Images and search will work, but if you modify the documentation sources, you have to issue this command again to see the changes.  Publish documentation online To generate and publish documentation online, say  sh fsb sdocs   This will publish the documentation to the  gh-pages branch in the online GitHub repository  among/fusus , from where it can be accessed by [https: among.github.io/fusus/](https: among.github.io/fusus/).  Push everything To generate and publish code and/or documentation and to push all changes to the  main branch in the online GitHub directory, say  sh fsb ship \"commit message\"   You have to provide a commit message."
},
{
"ref":"fusus.about.rationale",
"url":15,
"doc":" Rationale We skectch the academic background of this project. Medieval Arabic texts, especially those from intellectual history (philosophy, natural theology, theoretical mysticism) are sorely underrepresented in current digital text databases (such as al-Maktaba al-Shamela and Noorlib). There are, however, many (critical or not so critical) editions available of these texts. We therefore wanted to advance the use of printed editions to automatically create digital texts. Commentary writing is the practice of taking an earlier text and interspersing it with additional text. A commentary tradition is the standardization of such a practice on a given earlier text. This phenomenon is widely perceived in late medieval and early modern Islamic intellectual history. Ibn Arabi\u2019s Fusus al-hikam is an example of such a source text, on which dozens, perhaps hundreds, of commentaries were written through the centuries."
},
{
"ref":"fusus.about.howto",
"url":16,
"doc":" Install and update  code and documentation  fusus.about.install  get code  update docs  update code  Run  Straight from the command line  fusus.convert  run the OCR pipeline from the command line  run the PDF extraction from the command line  convert TSV to TF  Contribute more sources  From \"no comments\" to \"more comments\"  fusus.works  add commentaries as works  Explore  Page by page in a notebook  [do](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/do.ipynb) Run the pipeline in a notebook;  [inspect](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/inspect.ipynb) Inspect intermediate results in a notebook.  [ocr](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/ocr.ipynb) Read the proofs of Kraken-OCR.  [notebooks on nbviewer](https: nbviewer.jupyter.org/github/among/fusus/tree/master/notebooks/). All notebooks.  Tweak  Sickness and cure by parameters  [tweak](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/tweak.ipynb) Basic parameter tweaking;   fusus.parameters All parameters.  [comma](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/comma.ipynb) A ministudy in cleaning: tweak mark templates and parameters to wipe commas.  [lines](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/lines.ipynb) Follow the line detection algorithm in a wide variety of cases.  [piece](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/piece.ipynb) What to do if you have an image that is a small fragment of a page.  Engineer  Change the flow   fusus.lakhnawi PDF reverse engineering.  [pages](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/Lakhnawi/pages.ipynb) Work with pages, follow line division, extract text and save to disk.  [characters](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/Lakhnawi/characters.ipynb) See which characters are in the PDF and how they are converted.  [final](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/Lakhnawi/final.ipynb) See in the effect of final characters on spacing.  [border](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/example/border.ipynb) See how black borders get removed from a page. See also  fusus.lib.cropBorders and  fusus.lib.removeBorders .  Work  Do data science with the results  [useTsv](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/useTsv.ipynb) Use the TSV output of the pipeline.  [useTf](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/useTf.ipynb) Use the Text-Fabric output of the pipeline.  [boxes](https: nbviewer.jupyter.org/github/among/fusus/blob/master/notebooks/Lakhnawi/boxes.ipynb) Work with bounding boxes in the Text-Fabric data of the Lakhnawi."
},
{
"ref":"fusus.lines",
"url":17,
"doc":"Line detection We detect lines in page blocks based on ink distribution. Our proxy to ink distribution are histograms, but there is no easy correspondence between the peaks in the histograms and the lines on the page. We will need some signal processing tools from [SciPy](https: docs.scipy.org/doc/scipy/reference/), in particular [find_peaks](https: docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html scipy.signal.find_peaks) and [medfilt](https: docs.scipy.org/doc/scipy/reference/generated/scipy.signal.medfilt.html scipy.signal.medfilt), to filter the peaks into significant peaks. We also need to massage the ink histograms in order to correct for short lines."
},
{
"ref":"fusus.lines.getInkDistribution",
"url":17,
"doc":"Add line band data to all blocks based on histograms. By means of histograms we can discern where the lines are. We define several bands with respect to lines, such as main, inter, broad, high, mid, low. We also define a band for the space between lines. We mark the main bands on the  layout layer by a starting green line and an ending red line and the space between them will be overlaid with gray. Parameters      C: object Configuration settings stages: dict We need access to several intermediate results. pageH: int size of a full page in pixels blocks: dict The blocks as delivered by  getBlocks . The blocks dict will be updated: each block value gets a new key  bands with the band data. batch: boolean Whether we run in batch mode. boxed: boolean Whether we run in boxed mode (generate boxes around wiped marks). Returns    - list A list of keys in the blocks dict that correspond to blocks that turn out to be devoid of written material.",
"func":1
},
{
"ref":"fusus.lines.getInkX",
"url":17,
"doc":"Make a horizontal histogram of an input region of interest. Optionally draw the histograms on the corresponding roi of an output image. Parameters      imgIn: np array Input image. top, bottom, left, right: int Region of interest on input and output image. imgOut: np array, optional  None Output image. Returns    - histX: list The X histogram",
"func":1
},
{
"ref":"fusus.lines.firstNonzero",
"url":17,
"doc":"",
"func":1
},
{
"ref":"fusus.lines.lastNonzero",
"url":17,
"doc":"",
"func":1
},
{
"ref":"fusus.lines.getHist",
"url":17,
"doc":"",
"func":1
},
{
"ref":"fusus.lines.getInkY",
"url":17,
"doc":"Determine the line distribution in a block of text. Optionally draw the histogram and the peaks and valleys on the corresponding roi of an output image. In this operation, we determine the regular line height by analysing the peaks and the distances between them. But if we have just one peak, we do not have distances. In those cases, we take the last line height that has been calculated. Parameters      C: object The configuration object of the book engine. info: function To write messages to the console imgIn: np array Input image. pageH: int size of a full page in pixels top, bottom, left, right: int Region of interest on input and output image. final: boolean When computing the layout of a page, we call this function to adjust the vertical sizes of blocks. This is a non-final call to this function. Later, we determine the lines per block, that is the final call. When debugging, it is handy to be able to distinguish the debug information generated by these calls. imgOut: np array, optional  None Output image. Returns    - lines: list The detected lines, given as a list of tuples of upper and lower y coordinates",
"func":1
},
{
"ref":"fusus.ocr",
"url":18,
"doc":"Kraken Arabic model: [OpenITI](https: github.com/OpenITI/OCR_GS_Data/blob/master/ara/abhath/arabic_generalized.mlmodel) We can call Kraken with a batch of images. We can call binarization and segmentation and ocr in one call, but then we do not get the line segmentation json file. So we split it up in three batch calls: one for binarize, one for segmentation, and one for ocr. Alternatively, we can do binarization and segmentation in our preprocessing, and use Kraken for OCR only."
},
{
"ref":"fusus.ocr.getProofColor",
"url":18,
"doc":"",
"func":1
},
{
"ref":"fusus.ocr.showConf",
"url":18,
"doc":"",
"func":1
},
{
"ref":"fusus.ocr.OCR",
"url":18,
"doc":"Sets up OCR with Kraken."
},
{
"ref":"fusus.ocr.OCR.ensureLoaded",
"url":18,
"doc":"",
"func":1
},
{
"ref":"fusus.ocr.OCR.read",
"url":18,
"doc":"Perfoms OCR with Kraken.",
"func":1
},
{
"ref":"fusus.ocr.OCR.proofing",
"url":18,
"doc":"Produces an OCR proof page",
"func":1
},
{
"ref":"fusus.ocr.removeMargins",
"url":18,
"doc":"",
"func":1
},
{
"ref":"fusus.ocr.addWord",
"url":18,
"doc":"",
"func":1
},
{
"ref":"fusus.parameters",
"url":19,
"doc":"Settings and configuration"
},
{
"ref":"fusus.parameters.HOME",
"url":19,
"doc":"Full path to your home directory."
},
{
"ref":"fusus.parameters.BASE",
"url":19,
"doc":"Local directory where all your local clones of GitHub repositories are stored."
},
{
"ref":"fusus.parameters.ORG",
"url":19,
"doc":"Organization on GitHub in which this code/data repository resides. This is also the name of the parent directory of your local clone of this repo."
},
{
"ref":"fusus.parameters.REPO",
"url":19,
"doc":"Name of this code/data repository."
},
{
"ref":"fusus.parameters.REPO_DIR",
"url":19,
"doc":"Directory of the local repo. This is where this repo resides on your computer. Note that we assume you have followed the convention that it is in your home directory, and then  github/among/fusus ."
},
{
"ref":"fusus.parameters.PROGRAM_DIR",
"url":19,
"doc":"The subdirectory in the repo that contains the  fusus Python package ."
},
{
"ref":"fusus.parameters.LOCAL_DIR",
"url":19,
"doc":"Subdirectory containing unpublished input material. This is material that we cannot make public in this repo. This directory is not pushed to the online repo, by virtue of its being in the  .gitignore of this repo. See also  UR_DIR ."
},
{
"ref":"fusus.parameters.SOURCE_DIR",
"url":19,
"doc":"Subdirectory containing source texts. Here are the sources that we cannot make public in this repo. See also  UR_DIR and  LOCAL_DIR ."
},
{
"ref":"fusus.parameters.UR_DIR",
"url":19,
"doc":"Subdirectory containing the public source texts. Here are the sources that we can make public in this repo. See also  SOURCE_DIR ."
},
{
"ref":"fusus.parameters.COLORS",
"url":19,
"doc":"Named colors."
},
{
"ref":"fusus.parameters.BAND_COLORS",
"url":19,
"doc":"Band colors. Each band will be displayed in its own color."
},
{
"ref":"fusus.parameters.STAGES",
"url":19,
"doc":"Stages in page processing. When we process a scanned page, we produce named intermediate stages, in this order. The stage data consists of the following bits of information:  kind: image or data (i.e. tab separated files with unicode data).  colored: True if colored, False if grayscale, None if not an image  extension: None if an image file, otherwise the extension of a data file, e.g.  tsv "
},
{
"ref":"fusus.parameters.SETTINGS",
"url":19,
"doc":"Customizable settings. These are the settings that can be customized in several ways. The values here are the default values. When the pipeline is run in a book directory, it will look for a file  parameters.yaml in the toplevel directory of the book where these settings can be overridden. In a program or notebook you can also make last-minute changes to these parameters by calling the  fusus.book.Book.configure method which calls the  Config.configure method. The default values can be inspected by expanding the source code.  ! caution \"Two-edged sword\" When you change a parameter to improve a particular effect on a particular page, it may wreak havoc with many other pages. When you tweak, take care that you do it locally, on a single book, or a single page. debug : Whether to show (intermediate) results. If  0 : shows nothing, if  1 : shows end result, if  2 : shows intermediate results. inDir : name of the subdirectory with page scans outDir : name of the subdirectory with the final results of the workflow interDir : name of the subdirectory with the intermediate results of the workflow cleanDir : name of the subdirectory with the cleaned, blockwise images of the workflow marksDir : name of the subdirectory with the marks skewBorder : the width of the page margins that will be whitened in order to suppress the sharp black triangles introduces by skewing the page blurX : the amount of blur in the X-direction. Blurring is needed to get better histograms To much blurring will hamper the binarization, see e.g. pag 102 in the examples directory: if you blur with 41, 41 binarization fails. blurY : the amount of blur in the X-direction. Blurring is needed to get betterskewing and histograms.  ! caution \"Amount of Y-blurring\" Too much vertical blurring will cause the disappearance of horizontal bars from the histogram. Footnote bars will go undetected. Too little vertical blurring will result in ragged histograms, from which it is difficult to get vertical line boundaries. marginThresholdX : used when interpreting horizontal histograms. When histograms for horizontal lines cross marginThresholdY, it will taken as an indication that a line boundary (upper or lower) has been reached. contourFactor : used when computing left and right contour lines of a page. Each horizontal line as a left most black pixel and a rightmost one. Together they form the left contour and the right contour of the page. The length of each line is the distance between the left contour and right contour points on that line. However, to be useful, the contour lines must be smoothed. We look up and down from each contour point and replace it by the median value of the contour points above and below that point. How far do we have to look? We want to neutralize the interline spaces, so we look up and down for a fraction line line height. That fraction is specified by this parameter. A proxy for the line height is the peak distance. peakSignificant : used when interpreting histograms for line detection When we look for significant peaks in a histogram, we determine the max peak height. Significant peaks are those that have a height greater than a specific fraction of the max peak height. This parameter states that fraction. peakTargetWidthFraction : used when interpreting histograms for line detection When we have studied the significant peaks and found the regular distance between successive peaks, we use that to pass as the  distance parameter to the SciPy [find_peaks](https: docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html scipy.signal.find_peaks) algorithm. We get the best results if we do not pass the line height itself, but a fraction of it. This parameter is that fraction. peakProminenceY, valleyProminenceY : used when interpreting histograms for line detection We detect peaks and valleys in the histogram by means of a SciPy algorithm, to which we pass a prominence parameter. This will leave out minor peaks and valleys. outerValleyShiftFraction : used when interpreting histograms for line detection The valleys at the outer ends of the histogram tend to be very broad and hence the valleys will be located too far from the actual ink. We correct for that by shifting those valleys a fraction of their plateau sizes towards the ink. This parameter is that fraction. defaultLineHeight : used for line detection After line detection, a value for the line height is found and stored in this parameter. The parameter is read when there is only one line on a page, in which case the line detection algorithm has too little information. If this occurs at the very first calculation of line heights, a fixed default value is used. accuracy : When marks are searched for in the page, we get the result in the form of a grayscale page where the value in each point reflects how much the page in that area resembles the mark. Only hits above the value of  accuracy will be considered. connectBorder : When marks are found, each hit will be inspected: is the ink in the hit connected to the ink outside the hit? This will be measured in an inner and outer border of the page, whose thickness is given by this parameter. connectThreshold : After computing inner and outer borders, they will be inverted, so that black has the maximum value. Then the inside and outside borders are multiplied pixel wise, so that places where they are both black get very high values. All places where this product is higher than the value of  connectThreshold are retained for further calculation. connectRatio : After computing the places where inner and outer borders contain joint ink, the ratio of such places with respect to the total border size is calculated. If that ratio is greater than  connectRatio , the hit counts as connected to its surroundings. We have not found a true instance of the mark, and the mark will not be cleaned. boxBorder : The hits after searching for marks will be indicated on the  boxed stage of the page by means of a small coloured border around each hit. The width of this border is  boxBorder . maxHits : When searching for marks, there are usually multiple hits: the place where the mark occurs, and some places very nearby. The cleaning algorithm will cluster nearby hits and pick the best hit per cluster. But if the number of hits is very large, it is a sign that the mark is not searched with the right accuracy, and clustering will be prevented. It would become very expensive, and useless anyway. A warning will be issued in such cases. bandMain : Offsets for the  main band. Given as  (top, bottom) , with  top and  bottom positive or negative integers. This band covers most of the ink in a line. The  main band is computed from the histogram after which the height of the top and bottom boundaries are adjusted relative to the values obtained by the histogram algorithm. You can adjust these values: higher values move the boundaries down, lower values move them up. In practice, the adjustments are zero for the main band, while all other bands are derived from the main band by applying adjustments. bandInter : Offsets for the  inter band. This band covers most of the white between two lines. The  inter band is computed from the histogram. bandBroad : Offsets for the  broad band. This band s like  main but covers even more ink in a line. bandMid : Offsets for the  mid band. This band s like  main but covers the densest part in a line. bandHigh : Offsets for the  high band. This band s like  inter but covers the upper part of the letters and the white space above it. bandLow : Offsets for the  low band. This band s like  inter but covers the lower part of the letters and the white space below it."
},
{
"ref":"fusus.parameters.LINE_CLUSTER_FACTOR",
"url":19,
"doc":"Clustering characters into lines in the Lakhnawi PDF. When the characters on a page are divided into lines based on their height, this parameter determines which heights can be clustered together. Heights that differ less than the estimated average line height times this factor, can be clustered together."
},
{
"ref":"fusus.parameters.Config",
"url":19,
"doc":"Settings manager. It will expose all settings as attributes to the rest of the application. It has methods to collect modified settings from the user and apply them. The default settings are kept as a separate copy that will not be changed in any way. User modifications act on the current settings, which have been obtained by deep-copying the defaults. Parameters      tm: object Can display timed info/error messages to the display params: dict key-value pairs that act as updates for the settings. If a value is  None , the original value will be reinstated."
},
{
"ref":"fusus.parameters.Config.configure",
"url":19,
"doc":"Updates current settings based on new values. User modifications act on the current settings, which have been obtained by deep-copying the defaults. Parameters      reset: boolean, optional  False If  True , a fresh deep copy of the defaults will be made and that will be the basis for the new current settings. params: dict key-value pairs that act as updates for the settings. If a value is  None , the original value will be reinstated.",
"func":1
},
{
"ref":"fusus.parameters.Config.show",
"url":19,
"doc":"Display current settings. Parameters      params: str, optional  None If  None , all settings will be displayed. Else it should be a comma-separated string of legal parameter names whose values are to be displayed.",
"func":1
},
{
"ref":"fusus.book",
"url":20,
"doc":"Book workflow We will transform scanned pages of a book into Unicode text following a number of processing steps.  The express way In the terminal,  cd to a book directory (see below) and run   python3 -m fusus.book   This will process all scanned pages with default settings.  With more control and feedback Copy the notebook  example/do.ipynb into a book directory (see below). Run cells in the notebook, and see [doExample](https: github.com/among/fusus/blob/master/example/doExample.ipynb) to learn by example how you can configure the processing parameters and control the processing of pages.  Book directory A book directory should have subdirectories at the outset:   in Contains image files (scans at 1800 x2700 pixels approximately);   marks (optional) Contains subdirectories with little rectangles copied from the scans and saved in individual files at the same resolution.  Marks Marks are spots that will be wiped clean wherever they are found. They are organized in  bands which are sets of horizontal strokes on the page, relative to the individual lines. Marks will only be searched for within the bands they belong to, in order to avoid false positives. The  marks directory may contain the following bands: name | kind | items | remarks  - |  - |  - |  -  high | marks | arbitrary images | in the upper band of a line  low | marks | arbitrary images | in the lower band of a line  mid | marks | arbitrary images | in the central, narrow band of a line, with lots of ink  main | marks | arbitrary images | in the band where nearly all the letter material is  broad | marks | arbitrary images | as  main , but a bit broader  inter | marks | arbitrary images | between the lines When fusus reads the marks, it will crop all white borders from it and surround the result with a fixed small white border. So you do not have to be very precise in trimming the mark templates. After running the pipeline, the following subdirectories may have been produced:   inter Intermediate files, such as page images with histograms displayed in it, or data files with information on the marks that have been encountered and wiped;   clean Cleaned page block images, input for OCR processing.   out Output (= final results). Tab separated files with one row per word.   proof Aids to assess the quality of the output. Tab separated files with one row per character. Normalized input images. Overlay HTML files with OCR results, coloured by confidence, both on character basis and on word basis.   text Plain HTML rendering of the full, recognized text with page and line indicators. Used for reading the results by human eyes.  ! caution \"Block information\" If the layout algorithm has divided the page into blocks, the information of the blocks resides in the page object and is not currently stored on disk. This information is needed after OCR to shift the coordinates with respect to the blocks 9this is what comes out of the OCR) to coordinates with respect to the page. That means you cannot initialize the pipeline with the clean block images as sole input. You have to start with layout detection."
},
{
"ref":"fusus.book.Book",
"url":20,
"doc":"Engine for book conversion. Parameters      cd: string, optional If passed, performs a change directory to the directory specified. Else the whole book processing takes place in the current directory. You can use  ~ to denote your home directory. params: dict, optional Any number of customizable settings from  fusus.parameters.SETTINGS . They will be in effect when running the workflow, until a  Book.configure action will modify them."
},
{
"ref":"fusus.book.Book.info",
"url":20,
"doc":"",
"func":1
},
{
"ref":"fusus.book.Book.warning",
"url":20,
"doc":"",
"func":1
},
{
"ref":"fusus.book.Book.error",
"url":20,
"doc":"",
"func":1
},
{
"ref":"fusus.book.Book.configure",
"url":20,
"doc":"Updates current settings based on new values. The signature is the same as  fusus.parameters.Config.configure .",
"func":1
},
{
"ref":"fusus.book.Book.showSettings",
"url":20,
"doc":"Display settings. Parameters      params: dict, optional Any number of customizable settings from  fusus.parameters.SETTINGS . The current values of given parameters will be displayed. The values that you give each of the  params here is not used, only their names. It is recommended to pass  None as values:  B.showSettings(blurX=None, blurY=None) ",
"func":1
},
{
"ref":"fusus.book.Book.availableBands",
"url":20,
"doc":"Display the characteristics of all defined  bands .",
"func":1
},
{
"ref":"fusus.book.Book.availableMarks",
"url":20,
"doc":"Display the characteristics of defined  marks . Parameters      band: string, optional  None Show only marks in this band. If  None , show marks in all bands. mark: string, optional  None Show only marks in with this name. If  None , show marks with any name.",
"func":1
},
{
"ref":"fusus.book.Book.availablePages",
"url":20,
"doc":"Display the amount and page numbers of all pages.",
"func":1
},
{
"ref":"fusus.book.Book.process",
"url":20,
"doc":"Process directory of images. Executes all processing steps for all images. Parameters      pages: string | int, optional  None Specification of pages to do. If absent or  None : all pages. If an int, do only that page. Otherwise it must be a comma separated string of (ranges of) page numbers. Half ranges are also allowed:  -10 (from beginning up to and including  10 ) and  10- (from 10 till end). E.g.  1 and  5-7 and  2-5,8-10 , and  -10,15-20,30- . No spaces allowed. batch: boolean, optional  True Whether to run in batch mode. In batch mode everything is geared to the final output. Less intermediate results are computed and stored. Less feedback happens on the console. boxed: boolean, optional  False If in batch mode, produce also images that display the cleaned marks in boxes. quiet: boolean, optional  True Whether to suppress warnings and the display of stroke separators. doOcr: boolean, optional  True Whether to perform OCR processing uptoLayout: boolean, optional  False Whether to stop after doing layout Returns    - A  fusus.page.Page object for the last page processed, which is the handle for further inspection of what has happened during processing.",
"func":1
},
{
"ref":"fusus.book.Book.stageDir",
"url":20,
"doc":"",
"func":1
},
{
"ref":"fusus.book.Book.measureQuality",
"url":20,
"doc":"Measure the reported quality of the ocr processing. pages: string | int, optional  None Specification of pages to do. If absent or  None : all pages. If an int, do only that page. Otherwise it must be a comma separated string of (ranges of) page numbers. Half ranges are also allowed:  -10 (from beginning up to and including  10 ) and  10- (from 10 till end). E.g.  1 and  5-7 and  2-5,8-10 , and  -10,15-20,30- . No spaces allowed. showStats: boolean, optional  True Compute and show quality statistics updateProofs: boolean, optional  False If true, regenerate all proofing pages. This is desriable if you have tweaked the coloring of OCR results depending on the confidence. The OCR itself does not have to be performed again for this.",
"func":1
},
{
"ref":"fusus.book.Book.exportTsv",
"url":20,
"doc":"Combine the tsv data per page to one big tsv file. pages: string | int, optional  None Specification of pages to do. If absent or  None : all pages. If an int, do only that page. Otherwise it must be a comma separated string of (ranges of) page numbers. Half ranges are also allowed:  -10 (from beginning up to and including  10 ) and  10- (from 10 till end). E.g.  1 and  5-7 and  2-5,8-10 , and  -10,15-20,30- . No spaces allowed. The output is written to the working directory.",
"func":1
},
{
"ref":"fusus.book.Book.plainText",
"url":20,
"doc":"Get the plain text from the ocr output in one file pages: string | int, optional  None Specification of pages to do. If absent or  None : all pages. If an int, do only that page. Otherwise it must be a comma separated string of (ranges of) page numbers. Half ranges are also allowed:  -10 (from beginning up to and including  10 ) and  10- (from 10 till end). E.g.  1 and  5-7 and  2-5,8-10 , and  -10,15-20,30- . No spaces allowed. The output is written to the  text subdirectory.",
"func":1
},
{
"ref":"fusus.book.main",
"url":20,
"doc":"Process a whole book with default settings. Go to the book directory and say   python3 -m fusus.book [pages]   where  pages is an optional string specifying ranges of pages as in  Book.process ",
"func":1
}
]