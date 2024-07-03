"""BACKEND.PY
This script answers your questions about Justin's modular code
Dependencies: `dotenv`, `langchain`, `langchain-community`, langchain-anthropic`,
"""

# Load libraries
import os
import argparse
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic



# Load data
load_dotenv(".env")
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]

def load_llm(key: str) -> ChatAnthropic:
    # create a prompt template
    template = """You are Justin, an expert Javascript developer who developed useful modular code to quickly create data visualizations with the D3.js library.
    Since you've created several thousands of lines of code, other developers on your team often have questions about how to accomplish certain tasks. 
    You methodically review only the content of the source code and documentation below to answer their questions. 
    You are modest and honest, saying "I don't know" when you can't answer a question using the source code or documentation and admitting when your code currently has no support for a feature. 

    A colleague asks you the following question:
    {question}

    Here is the relevant source code: 
    ```js
    {source}
    ```

    Here is the relevant documentation:
    ```md
    {documentation}
    ```

    Response to colleague:
    """
    
    prompt = PromptTemplate(input_variables=['question, source', 'documentation'], template=template)
    
    llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.7, 
                        max_tokens=2048, api_key=key)
    
    return prompt | llm
    

# Run search

def generate_answer(query : str, graph_type : str, llm : ChatAnthropic) -> str:
    source = ''
    documentation = ''
    
    if graph_type == 'bar':
        source = """/*

BAR.JS

This file has a class with methods related to creating a bar graph. 

Note that d3.js must be loaded before using this file.

The following methods can be used:
- BarGraph() - bar graph constructor 
- init() - sets up axis generators, scale functions, data - all together. 
- initData() - prepares raw data for rendering grouped and stacked bar graph.
- initCScale() - sets up scale function for categorical data axis
- initNScale() - sets up scale function for numerical data axis
- initAxes() - sets up axis generator functions
- initBarWidth() - computes width of each bar based on data and graph size
- clear() - removes the existing graph (visuals removed, settings remain)
- render() - displays the graph after settings have been configured

Also, the following fields are useful to adjust: 
- data/cSeries/categories - raw data as an array of objects and the keys showing
  the categorical/numerical data field of objects
- graphTitle/cAxisTitle/nAxisTitle - the titles to display on top of the graph
  and on each axis
- vertical - whether to have vertical bars or horizontal
- grouped - whether to have side-by-side bars in groups or to stack the bars
- container - an SVG element to render the bar graph in
- wrapper - a div element containing the SVG element
- width/height/margins - controls the size and proportions of the bar graph

*/

// import { textures } from "/src/js/textures.js";


export class BarGraph {
  // =============== DECLARE FIELDS ===================
  #data;
  #cSeries;
  #cKeys;
  #nKey; //only one key now
  #selectedCategories; //selected categories
  #colourSeries = [
    "#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#37A86F",
    "#edc949", "#af7aa1", "#ff9da7", "#9c755f", "#bab0ab",
    "#6b9ac4", "#d84b2a", "#8c8c8c", "#69cc58", "#e279a3",
    "#665191", "#f7b6d2", "#dbdb8d", "#bcbd22", "#17becf",
    "#9467bd", "#69312d", "#e377c2", "#c49c94",
  ]
  #textureSeries = [];
  #textureTypeSeries;
  #textures;
  #tooltipSeries;

  #categoryKey;
  #categories;

  #categoryLookup = {}
  #categoryReverseLookup = {}
  #graphTitle;
  #cAxisTitle;
  #nAxisTitle;
  #nAxisTickNumber;
  #nAxisNice = false;

  #cAxisTitleSpacing = 50;
  #nAxisTitleSpacing = 60;

  #hasRendered = false;

  #vertical = false;
  #grouped = false;
  #tooltips = false;
  #specificTooltip = false;
  #barLabels = false;
  #alwaysDisplayBarLabels = false;
  #displayStackedSums = false;
  #interactive = false;
  #loadAnimation = false; // functionality currently removed (can't toggle it off)
  #gridlines = false;
  #log = false;
  #proportional = false;
  #textContrastChecker = false; // functionality currently removed (can't toggle it off)
  #displayLegend = false;
  #hideLegendText = false;
  #displayUncertainties = false;
  #percent = false;
  #fitTickText = false;
  #detectLegendSpacing = false;
  #addCustomGroup = false;
  #captionAbove = false;
  #interactiveFixedAxis = false;

  #legendHoverFade = false;
  #barHoverFade = false;

  #htmlLegendHideSingle = false;

  #upperUncertainty;
  #lowerUncertainty;
  #uncertaintyWidth = 8;

  #averageLines;
  #averageLinesColours = ["black", "red", "orange"]
  #averageLinesType = ["solid", "dashed", "dashed"]
  #averageLinesLegendText;

  #decimalPlaces;
  #decimalType = 'round';

  #transitionDuration = 1000;

  //formatters
  #tableHeaderFunction;
  #tableCellFunction;
  #tooltipFunction;
  #nTickFormat;
  #cTickFormat;
  #labelFormat;

  //callbacks
  #callbackClick;
  #callbackHover;
  #callbackLegendHover;

  //Accessibility
  #figureAriaLabel = "Bargraph";
  #figureAriaDescription = 'Contains different bars. Press the "Enter" key to tab through the bar groups, and enter again to tab through bars within a group. To exit the graph, either tab through all the groups or press the "Escape" key';

  // #logMin = 0.001;
  #min;
  #max;

  /*
     things to add functionality for:
     - Allow barlabels to be toggled on/off between updates
     - Consider dynamically hiding text that does not fit in respective bar (currently thinking no, let graph maker decide whats right for graph)
  */

  #container;
  #wrapper;
  #barGroup;
  #legendGroup;
  #axesGroup;
  #titleGroup;
  #averageGroup;
  #customGroup;

  #htmlLegend;

  //table stuff
  #table;
  #tableCaption;
  #tableSummary = d3.select('html').attr('lang') == "fr" ? "Texte descriptif" : "Text description";
  #tableOrder;

  #isFrench = d3.select('html').attr('lang') == "fr" ? true : false;

  #axisGens;
  #stackGen;
  #stackData;
  #groupData;

  //private
  #proportionalStack;

  //scales
  #cScales = [];
  #nScale;
  #colourScale;
  #noCategoryColourScale;

  // #surGroups = [];
  #surKeys = [];
  // #surScales = [];
  #cSubScale;

  #cAxisInitialHeight = 0; //90
  #cAxisDrop = 0; //45

  #width = 720;
  #height = 480;
  #margins = { l: 100, r: 60, t: 60, b: 100 };
  #defaultPadding = 0.25;
  #subPadding;
  #cPaddingSeries;

  #barWidth;
  #legendRadius = 8;
  #legendTextOffset = 15;
  #legendCircleSpacing = 28;
  #legendSecondaryCircleSpacing = 28;
  #legendSpacingFromGraph = 20;
  #legendOrientation = 'v';
  #legendPosition;
  #legendItemWrapCounter;
  #legendInteractionType = 'toggle';

  //#region =============== CHAINING METHODS - with validation ===================
  data(inputData) {
    /*
    Parameters 
    ----------------
    inputData (type: array)
      - An array of object(s) with 2+ fields per object
      - Each object represents one row of data. Each field represents a column
    */
    if (arguments.length === 0) {
      return this.#data;
    }
    else {
      // Check input
      const nonEmptyArray = (typeof inputData == typeof []) &&
        (inputData.length > 0);
      let validElements = true;

      if (nonEmptyArray) {
        for (let v of inputData) {
          if ((typeof v != typeof {}) ||
            Object.keys(v).length < 2) {

            validElements = false;
            break;
          }
        }
      }

      // Set field
      if (nonEmptyArray && validElements) {
        this.#data = inputData;
        return this;
      }
      else {
        console.error('Data must be an array of object(s) with 2+ fields');
      }
    }
  }
  nKey(inputKey) {
    /*
    Parameters 
    ----------------
    inputKey (type: string)
      - A string representing a key that the data field has. 
      - This string should indicate the key (data header) for the dependent variable
    */
    if (arguments.length === 0) {
      return this.#nKey;
    }
    else {

      const validString = (typeof inputKey == typeof 'abc') && inputKey;

      if (validString) {
        this.#nKey = inputKey;
        return this;
      }
      else {
        console.error('nKey must be a non-empty string');
      }
    }
  }
  cSeries(inputKeys) {
    /*
    Parameters 
    ----------------
    inputKeys (type: array)
      - An array of string(s) representing key(s) that the data field has. 
      - This array should indicate some key(s) to use for the numerical axis
    */

    if (arguments.length === 0) {
      return this.#cSeries;
    }
    else {
      // Check input
      const nonEmptyArray = (typeof inputKeys == typeof []) &&
        (inputKeys.length > 0);
      let validElements = true;

      if (nonEmptyArray) {
        for (let v of inputKeys) {
          if ((typeof v != typeof 'abc') || !v) {
            validElements = false;
            break;
          }
        }
      }

      // Set field
      if (nonEmptyArray && validElements) {
        this.#cSeries = inputKeys;
        return this;
      }
      else {
        console.error('cSeries must be an array of non-empty string(s)');
      }
    }
  }
  categoryKey(inputKey) {
    /*
    Parameters 
    ----------------
    inputKey (type: string)
      - A string representing a key that the data field has. 
      - This string should indicate the key (data header) for the dependent variable
    */
    // if (arguments.length === 0) {
    //   return this.#categoryKey;
    // }
    // else {

    //   const validString = (typeof inputKey == typeof 'abc') && inputKey;

    //   if (validString) {
    //     this.#categoryKey = inputKey;
    //     return this;
    //   }
    //   else {
    //     console.error('categoryKey must be a non-empty string');
    //   }
    // }
    if (arguments.length === 0) {
      return this.#categoryKey;
    }
    else {
      this.#categoryKey = inputKey;
      return this;
    }
  }
  selectedCategories(inputKeys) {
    /*
    Parameters 
    ----------------
    inputKeys (type: array)
      - An array of string(s) representing key(s) that the data field has currently selected. 
      - This array should indicate some key(s) to use for the numerical axis
    */

    if (arguments.length === 0) {
      return this.#selectedCategories;
    }
    else {
      // Check input
      const nonEmptyArray = (typeof inputKeys == typeof []) &&
        (inputKeys.length > 0);
      let validElements = true;

      if (nonEmptyArray) {
        for (let v of inputKeys) {
          if ((typeof v != typeof 'abc') || !v) {
            validElements = false;
            break;
          }
        }
      }

      // Set field
      if (nonEmptyArray && validElements) {
        this.#selectedCategories = inputKeys;
        return this;
      }
      else {
        console.error('selectedCategories must be an array of non-empty string(s)');
      }
    }
  }
  colourSeries(inputKeys) {
    /*
    Parameters 
    ----------------
    inputKeys (type: array)
      - An array of string(s) representing key(s) that the data field has currently selected. 
      - This array should indicate some key(s) to use for the numerical axis
    */

    if (arguments.length === 0) {
      return this.#colourSeries;
    }
    else {
      // Check input
      const nonEmptyArray = (typeof inputKeys == typeof []) &&
        (inputKeys.length > 0);
      let validElements = true;

      if (nonEmptyArray) {
        for (let v of inputKeys) {
          if ((typeof v != typeof 'abc') || !v) {
            validElements = false;
            break;
          }
        }
      }

      // Set field
      if (nonEmptyArray && validElements) {
        this.#colourSeries = inputKeys;
        return this;
      }
      else {
        console.error('colourSeries must be an array of non-empty string(s)');
      }
    }
  }
  textures(input) {
    if (arguments.length === 0) {
      return this.#textures;
    }
    else {
      this.#textures = input
      try {
        textures;
      }
      catch {
        console.error('Textures are not defined. They must be loaded in from "/src/js/textures.js" before your own script using the bar.js module. Ex: "<script src="/src/js/textures.js"></script>"')
      }

      return this;
    }
  }
  textureSeries(input) {
    if (arguments.length === 0) {
      return this.#textureSeries;
    }
    else {
      this.#textureSeries = input
      return this;
    }
  }
  textureTypeSeries(inputKeys) {
    /*
    Parameters 
    ----------------
    inputKeys (type: array)
      - An array of string(s) representing key(s) that denote which lines are dashed, dotted, straight
    */

    let accepted = ["solid", "grid", "dots", "diagonal"]

    if (arguments.length === 0) {
      return this.#textureTypeSeries;
    }
    else {
      // Check input
      const nonEmptyArray = (typeof inputKeys == typeof []) &&
        (inputKeys.length > 0);
      let validElements = true;

      if (nonEmptyArray) {
        for (let v of inputKeys) {
          if ((typeof v != typeof 'abc') || !v || !accepted.includes(v)) {
            validElements = false;
            break;
          }
        }
      }

      // Set field
      if (nonEmptyArray && validElements) {
        this.#textureTypeSeries = inputKeys;
        return this;
      }
      else {
        console.error(`textureTypeSeries must be an array of non-empty string(s) where the options are: ${accepted}`);
      }
    }
  }
  tooltipSeries(inputKeys) {
    /*
    Parameters 
    ----------------
    inputKeys (type: array)
      - An array of string(s) representing key(s) that the data field has. 
      - This array should indicate some key(s) to use for the tooltips
    */

    if (arguments.length === 0) {
      return this.#tooltipSeries;
    }
    else {
      // Check input
      const nonEmptyArray = (typeof inputKeys == typeof []) &&
        (inputKeys.length > 0);
      let validElements = true;

      if (nonEmptyArray) {
        for (let v of inputKeys) {
          if ((typeof v != typeof 'abc') || !v) {
            validElements = false;
            break;
          }
        }
      }

      // Set field
      if (nonEmptyArray && validElements) {
        this.#tooltipSeries = inputKeys;
        return this;
      }
      else {
        console.error('tooltipSeries must be an array of non-empty string(s)');
      }
    }
  }
  graphTitle(inputTitle) {
    /*
    Parameters 
    ----------------
    inputTitle (type: string)
      - A string containing the title for the graph. 
    */

    if (arguments.length === 0) {
      return this.#graphTitle;
    }
    else {
      const validString = (typeof inputTitle == typeof 'abc') && inputTitle;

      if (validString) {
        this.#graphTitle = inputTitle;
        return this;
      }
      else {
        console.error('graphTitle must be a non-empty string');
      }
    }
  }
  cAxisTitle(inputTitle) {
    /*
    Parameters 
    ----------------
    inputTitle (type: string)
      - A string containing the title for the categorical axis. 
    */

    if (arguments.length === 0) {
      return this.#cAxisTitle;
    }
    else {
      const validString = (typeof inputTitle == typeof 'abc');

      if (validString) {
        this.#cAxisTitle = inputTitle;
        return this;
      }
      else {
        console.error('cAxisTitle must be a string');
      }
    }
  }
  nAxisTitle(inputTitle) {
    /*
    Parameters 
    ----------------
    inputTitle (type: string)
      - A string containing the title for the numerical axis. 
    */

    if (arguments.length === 0) {
      return this.#nAxisTitle;
    }
    else {
      const validString = (typeof inputTitle == typeof 'abc');

      if (validString) {
        this.#nAxisTitle = inputTitle;
        return this;
      }
      else {
        console.error('nAxisTitle must be a string');
      }
    }
  }
  cAxisTitleSpacing(inputSpacing) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing from the cAxis.
    */
    if (arguments.length === 0) {
      return this.#cAxisTitleSpacing;
    }
    else {
      const validNum = (typeof inputSpacing == typeof 5) &&
        (inputSpacing >= 0);

      if (validNum) {
        this.#cAxisTitleSpacing = inputSpacing;
        return this;
      }
      else {
        console.error('cAxisTitleSpacing must be a number');
      }
    }
  }
  nAxisTitleSpacing(inputSpacing) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing from the cAxis.
    */
    if (arguments.length === 0) {
      return this.#nAxisTitleSpacing;
    }
    else {
      const validNum = (typeof inputSpacing == typeof 5) &&
        (inputSpacing >= 0);

      if (validNum) {
        this.#nAxisTitleSpacing = inputSpacing;
        return this;
      }
      else {
        console.error('nAxisTitleSpacing must be a number');
      }
    }
  }
  nAxisTickNumber(input) {
    if (arguments.length === 0) {
      return this.#nAxisTickNumber;
    }
    else {
      this.#nAxisTickNumber = input;
      return this;
    }
  }
  nAxisNice(input) {
    if (arguments.length === 0) {
      return this.#nAxisNice;
    }
    else {
      this.#nAxisNice = input;
      return this;
    }
  }

  decimalPlaces(input) {
    /*
    Parameters 
    ----------------
    input (type: number)
      - Number of decimal places.
    */
    if (arguments.length === 0) {
      return this.#decimalPlaces;
    }
    else {
      const validNum = (typeof input == typeof 5) &&
        (input >= 0);

      if (validNum) {
        this.#decimalPlaces = input;
        return this;
      }
      else {
        console.error('decimalPlaces must be a number');
      }
    }
  }
  decimalType(input) {
    /*
    Parameters 
    ----------------
    input (type: number)
      - Number of decimal places.
    */
    let accepted = ['round', 'fixed']
    if (arguments.length === 0) {
      return this.#decimalType;
    }
    else {
      const valid = (typeof input == typeof 'abc' && accepted.includes(input.toLowerCase()));

      if (valid) {
        this.#decimalType = input;
        return this;
      }
      else {
        console.error('decimalType must be either "round" or "fixed"');
      }
    }
  }
  vertical(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have vertical bars. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#vertical;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#vertical = inputToggle;
        return this;
      }
      else {
        console.error('vertical must be a boolean');
      }
    }
  }
  grouped(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have grouped bars. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#grouped;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#grouped = inputToggle;
        return this;
      }
      else {
        console.error('grouped must be a boolean');
      }
    }
  }
  tooltips(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have tooltips. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#tooltips;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#tooltips = inputToggle;
        return this;
      }
      else {
        console.error('tooltips must be a boolean');
      }
    }
  }
  specificTooltip(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have tooltips. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#specificTooltip;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#specificTooltip = inputToggle;
        return this;
      }
      else {
        console.error('specificTooltip must be a boolean');
      }
    }
  }
  barLabels(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have barLabels. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#barLabels;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#barLabels = inputToggle;
        return this;
      }
      else {
        console.error('barLabels must be a boolean');
      }
    }
  }
  alwaysDisplayBarLabels(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph alwaysDisplayBarLabels. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#alwaysDisplayBarLabels;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#alwaysDisplayBarLabels = inputToggle;
        return this;
      }
      else {
        console.error('alwaysDisplayBarLabels must be a boolean');
      }
    }
  }
  displayStackedSums(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have StackedSums. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#displayStackedSums;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#displayStackedSums = inputToggle;
        return this;
      }
      else {
        console.error('displayStackedSums must be a boolean');
      }
    }
  }
  interactive(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph interactive. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#interactive;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#interactive = inputToggle;
        return this;
      }
      else {
        console.error('interactive must be a boolean');
      }
    }
  }
  interactiveFixedAxis(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph not change the nAxis on interaction. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#interactiveFixedAxis;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#interactiveFixedAxis = inputToggle;
        return this;
      }
      else {
        console.error('interactiveFixedAxis must be a boolean');
      }
    }
  }
  loadAnimation(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have a loading animation. False otherwise.
    */
    if (arguments.length === 0) {
      return this.#loadAnimation;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#loadAnimation = inputToggle;
        return this;
      }
      else {
        console.error('loadAnimation must be a boolean');
      }
    }
  }
  gridlines(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have gridlines. False otherwise.
    */

    if (arguments.length === 0) {
      return this.#gridlines;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#gridlines = inputToggle;
        return this;
      }
      else {
        console.error('gridlines must be a boolean');
      }
    }
  }
  log(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have a logarithmic scale
    */

    if (arguments.length === 0) {
      return this.#log;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#log = inputToggle;
        return this;
      }
      else {
        console.error('log must be a boolean');
      }
    }
  }
  proportional(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have a logarithmic scale
    */

    if (arguments.length === 0) {
      return this.#proportional;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#proportional = inputToggle;
        return this;
      }
      else {
        console.error('proportional must be a boolean');
      }
    }
  }
  displayLegend(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph displayLegend
    */

    if (arguments.length === 0) {
      return this.#displayLegend;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#displayLegend = inputToggle;
        return this;
      }
      else {
        console.error('displayLegend must be a boolean');
      }
    }
  }
  hideLegendText(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph hideLegendText
    */

    if (arguments.length === 0) {
      return this.#hideLegendText;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#hideLegendText = inputToggle;
        return this;
      }
      else {
        console.error('hideLegendText must be a boolean');
      }
    }
  }
  htmlLegendHideSingle(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph htmlLegendHideSingle
    */

    if (arguments.length === 0) {
      return this.#htmlLegendHideSingle;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#htmlLegendHideSingle = inputToggle;
        return this;
      }
      else {
        console.error('htmlLegendHideSingle must be a boolean');
      }
    }
  }
  displayUncertainties(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have gridlines. False otherwise.
    */

    if (arguments.length === 0) {
      return this.#displayUncertainties;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#displayUncertainties = inputToggle;
        if ((!this.#upperUncertainty || !this.#lowerUncertainty) && inputToggle) {
          console.warn("lowerUncertainty and upperuncertainty keys must both be set for them to display")
        }
        return this;
      }
      else {
        console.error('displayUncertainties must be a boolean');
      }
    }
  }
  percent(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph have gridlines. False otherwise.
    */

    if (arguments.length === 0) {
      return this.#percent;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#percent = inputToggle;
        return this;
      }
      else {
        console.error('percent must be a boolean');
      }
    }
  }
  fitTickText(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph tick text wrap/shrink to fit size.
    */

    if (arguments.length === 0) {
      return this.#fitTickText;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#fitTickText = inputToggle;
        return this;
      }
      else {
        console.error('fitTickText must be a boolean');
      }
    }
  }
  detectLegendSpacing(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph tick text wrap/shrink to fit size.
    */

    if (arguments.length === 0) {
      return this.#detectLegendSpacing;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#detectLegendSpacing = inputToggle;
        return this;
      }
      else {
        console.error('detectLegendSpacing must be a boolean');
      }
    }
  }
  addCustomGroup(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph tick text wrap/shrink to fit size.
    */

    if (arguments.length === 0) {
      return this.#addCustomGroup;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#addCustomGroup = inputToggle;
        return this;
      }
      else {
        console.error('addCustomGroup must be a boolean');
      }
    }
  }
  captionAbove(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph tick text wrap/shrink to fit size.
    */

    if (arguments.length === 0) {
      return this.#captionAbove;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#captionAbove = inputToggle;
        return this;
      }
      else {
        console.error('captionAbove must be a boolean');
      }
    }
  }
  legendHoverFade(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph tick text wrap/shrink to fit size.
    */

    if (arguments.length === 0) {
      return this.#legendHoverFade;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#legendHoverFade = inputToggle;
        return this;
      }
      else {
        console.error('legendHoverFade must be a boolean');
      }
    }
  }
  barHoverFade(inputToggle) {
    /*
    Parameters 
    ----------------
    inputToggle (type: bool)
      - True to make the graph tick text wrap/shrink to fit size.
    */

    if (arguments.length === 0) {
      return this.#barHoverFade;
    }
    else {
      const validBool = (typeof inputToggle == typeof true);

      if (validBool) {
        this.#barHoverFade = inputToggle;
        return this;
      }
      else {
        console.error('barHoverFade must be a boolean');
      }
    }
  }

  legendRadius(inputRadius) {
    /*
    Parameters 
    ----------------
    inputRadius (type: number)
      - A non-negative number for the radius of the legend circles.
    */
    if (arguments.length === 0) {
      return this.#legendRadius;
    }
    else {
      const validNum = (typeof inputRadius == typeof 5) &&
        (inputRadius >= 0);

      if (validNum) {
        this.#legendRadius = inputRadius;
        return this;
      }
      else {
        console.error('legendRadius must be a non-negative number');
      }
    }
  }
  legendTextOffset(inputOffset) {
    /*
    Parameters 
    ----------------
    inputOffset (type: number)
      - A number for the space between text and the legend circles.
    */
    if (arguments.length === 0) {
      return this.#legendTextOffset;
    }
    else {
      const validNum = (typeof inputOffset == typeof 5);

      if (validNum) {
        this.#legendTextOffset = inputOffset;
        return this;
      }
      else {
        console.error('legendTextOffset must be a number');
      }
    }
  }
  legendCircleSpacing(inputSpacing) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing between legend circles.
    */
    if (arguments.length === 0) {
      return this.#legendCircleSpacing;
    }
    else {
      const validNum = (typeof inputSpacing == typeof 5);

      if (validNum) {
        this.#legendCircleSpacing = inputSpacing;
        return this;
      }
      else {
        console.error('legendCircleSpacing must be a number');
      }
    }
  }
  legendSecondaryCircleSpacing(inputSpacing) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing between legend circles.
    */
    if (arguments.length === 0) {
      return this.#legendSecondaryCircleSpacing;
    }
    else {
      const validNum = (typeof inputSpacing == typeof 5);

      if (validNum) {
        this.#legendSecondaryCircleSpacing = inputSpacing;
        return this;
      }
      else {
        console.error('legendSecondaryCircleSpacing must be a number');
      }
    }
  }
  legendSpacingFromGraph(inputSpacing) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing between the graph and the legend.
    */
    if (arguments.length === 0) {
      return this.#legendSpacingFromGraph;
    }
    else {
      const validNum = (typeof inputSpacing == typeof 5);

      if (validNum) {
        this.#legendSpacingFromGraph = inputSpacing;
        return this;
      }
      else {
        console.error('legendCircleSpacing must be a number');
      }
    }
  }
  legendItemWrapCounter(inputSpacing) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing between the graph and the legend.
    */
    if (arguments.length === 0) {
      return this.#legendItemWrapCounter;
    }
    else {
      const validNum = (typeof inputSpacing == typeof 5);

      if (validNum) {
        this.#legendItemWrapCounter = inputSpacing;
        return this;
      }
      else {
        console.error('legendItemWrapCounter must be a number');
      }
    }
  }

  upperUncertainty(inputKey) {
    /*
    Parameters 
    ----------------
    inputKey (type: string)
      - A string representing a key that the data field has. 
      - This string should indicate the key (data header) for the dependent variable
    */
    if (arguments.length === 0) {
      return this.#upperUncertainty;
    }
    else {

      const validString = (typeof inputKey == typeof 'abc') && inputKey;

      if (validString) {
        this.#upperUncertainty = inputKey;
        return this;
      }
      else {
        console.error('upperUncertainty must be a non-empty string');
      }
    }
  }
  lowerUncertainty(inputKey) {
    /*
    Parameters 
    ----------------
    inputKey (type: string)
      - A string representing a key that the data field has. 
      - This string should indicate the key (data header) for the dependent variable
    */
    if (arguments.length === 0) {
      return this.#lowerUncertainty;
    }
    else {

      const validString = (typeof inputKey == typeof 'abc') && inputKey;

      if (validString) {
        this.#lowerUncertainty = inputKey;
        return this;
      }
      else {
        console.error('lowerUncertainty must be a non-empty string');
      }
    }
  }
  uncertaintyWidth(input) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing from the cAxis.
    */
    if (arguments.length === 0) {
      return this.#uncertaintyWidth;
    }
    else {
      const validNum = (typeof input == typeof 5) &&
        (input >= 0);

      if (validNum) {
        this.#uncertaintyWidth = input;
        return this;
      }
      else {
        console.error('uncertaintyWidth must be a number');
      }
    }
  }

  legendOrientation(input) {
    /*
    Parameters 
    ----------------
    input (type: char)
      - A number for the spacing between the graph and the legend.
    */
    if (arguments.length === 0) {
      return this.#legendOrientation;
    }
    else {
      const valid = (typeof input == typeof 'a');

      if (valid) {
        this.#legendOrientation = input;
        return this;
      }
      else {
        console.error('legendOrientation must be "v" for vertical, or "h" for horizontal');
      }
    }
  }
  legendInteractionType(input) {
    /*
    Parameters 
    ----------------
    input (type: char)
      - A number for the spacing between the graph and the legend.
    */
    let accepted = ['toggle', 'isolate']

    if (arguments.length === 0) {
      return this.#legendInteractionType;
    }
    else {
      const valid =
        // (typeof input == typeof 'a') && 
        accepted.includes(input);

      if (valid) {
        this.#legendInteractionType = input;
        return this;
      }
      else {
        console.error('legendInteractionType must be either "toggle" or "isolate"');
      }
    }
  }
  legendPosition(input) {
    /*
    Parameters 
    ----------------
    input (type: array)
      - [x, y] position of legend
    */
    if (arguments.length === 0) {
      return this.#legendPosition;
    }
    else {
      this.#legendPosition = input;
      return this;
    }
  }

  transitionDuration(input) {
    if (arguments.length === 0) {
      return this.#transitionDuration;
    }
    else {
      const validNum = (typeof input == typeof 5) &&
        (input >= 0);

      if (validNum) {
        this.#transitionDuration = input;
        return this;
      }
      else {
        console.error('transitionDuration must be a non-negative number');
      }
    }
  }
  barWidth(inputBarWidth) {
    /*
    Parameters 
    ----------------
    inputBarWidth (type: number)
      - A non-negative number for the width of bars.
    */
    if (arguments.length === 0) {
      return this.#barWidth;
    }
    else {
      const validNum = (typeof inputBarWidth == typeof 5) &&
        (inputBarWidth >= 0);

      if (validNum) {
        this.#barWidth = inputBarWidth;
        return this;
      }
      else {
        console.error('barWidth must be a non-negative number');
      }
    }
  }
  cAxisInitialHeight(inputSpacing) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing between the graph and the legend.
    */
    if (arguments.length === 0) {
      return this.#cAxisInitialHeight;
    }
    else {
      const validNum = (typeof inputSpacing == typeof 5);

      if (validNum) {
        this.#cAxisInitialHeight = inputSpacing;
        return this;
      }
      else {
        console.error('cAxisInitialHeight must be a number');
      }
    }
  }
  cAxisDrop(inputSpacing) {
    /*
    Parameters 
    ----------------
    inputSpacing (type: number)
      - A number for the spacing between the graph and the legend.
    */
    if (arguments.length === 0) {
      return this.#cAxisDrop;
    }
    else {
      const validNum = (typeof inputSpacing == typeof 5);

      if (validNum) {
        this.#cAxisDrop = inputSpacing;
        return this;
      }
      else {
        console.error('cAxisDrop must be a number');
      }
    }
  }
  width(inputWidth) {
    /*
    Parameters 
    ----------------
    inputWidth (type: number)
      - A non-negative number for the width of the bar graph.
    */
    if (arguments.length === 0) {
      return this.#width;
    }
    else {
      const validNum = (typeof inputWidth == typeof 5) &&
        (inputWidth >= 0);

      if (validNum) {
        this.#width = inputWidth;
        return this;
      }
      else {
        console.error('width must be a non-negative number');
      }
    }
  }
  height(inputHeight) {
    /*
    Parameters 
    ----------------
    inputHeight (type: number)
      - A non-negative number for the height of the bar graph. 
    */

    if (arguments.length === 0) {
      return this.#height;
    }
    else {
      const validNum = (typeof inputHeight == typeof 5) &&
        (inputHeight >= 0);

      if (validNum) {
        this.#height = inputHeight;
        return this;
      }
      else {
        console.error('height must be a non-negative number');
      }
    }
  }
  margins(inputMargins) {
    /*
    Parameters 
    ----------------
    inputMargins (type: array)
      - An array of numbers representing margins between the 
        bar graph and the SVG container. 
      - Specify margins in clockwise order (top, right, bottom, left)
    */
    if (arguments.length === 0) {
      return this.#margins;
    }
    else {
      // Validate nums
      let validNums = true;
      for (let n of inputMargins) {
        if (typeof n != typeof 5) {
          validNums = false;
          break;
        }
      }

      // Set fields
      if (validNums) {
        this.#margins = {
          l: inputMargins[3],
          r: inputMargins[1],
          t: inputMargins[0],
          b: inputMargins[2]
        };
        return this;
      }
      else {
        console.error(
          'Please input an array of four numbers to configure top,' +
          'right, bottom, and left margins in that order.'
        );
      }
    }
  }
  defaultPadding(inputPadding) {
    /*
    Parameters 
    ----------------
    inputPadding (type: number)
      - A number between 0 and 1 that represents a decimal percentage. 
      - This should indicate what percent of a bar's width should 
        be cut away for padding.
    */
    if (arguments.length === 0) {
      return this.#defaultPadding;
    }
    else {
      const validNum = (typeof inputPadding == typeof 5) &&
        (inputPadding <= 1) && (inputPadding >= 0);

      if (validNum) {
        this.#defaultPadding = inputPadding;
        return this;
      }
      else {
        console.error('defaultPadding must be a decimal number between 0-1');
      }
    }
  }
  cPaddingSeries(input) {
    if (arguments.length === 0) {
      return this.#cPaddingSeries;
    }
    else {
      this.#cPaddingSeries = input;
      return this;
    }
  }
  subPadding(inputSubPadding) {
    /*
    Parameters 
    ----------------
    inputSubPadding (type: number)
      - A number between 0 and 1 that represents a decimal percentage. 
      - This should indicate what percent of a bar's width should 
        be cut away for padding.
    */
    if (arguments.length === 0) {
      return this.#subPadding;
    }
    else {
      const validNum = (typeof inputSubPadding == typeof 5) &&
        (inputSubPadding <= 1) && (inputSubPadding >= 0);

      if (validNum) {
        this.#subPadding = inputSubPadding;
        return this;
      }
      else {
        console.error('subPadding must be a decimal number between 0-1');
      }
    }
  }
  tableCaption(inputCaption) {
    /*
    Parameters 
    ----------------
    inputCaption (type: string)
      - A string containing the caption for the table. 
    */

    if (arguments.length === 0) {
      return this.#tableCaption;
    }
    else {
      const validString = (typeof inputCaption == typeof 'abc') && inputCaption;

      if (validString) {
        this.#tableCaption = inputCaption;
        return this;
      }
      else {
        console.error('tableCaption must be a non-empty string');
      }
    }
  }
  tableSummary(inputSummary) {
    /*
    Parameters 
    ----------------
    inputCaption (type: string)
      - A string containing the caption for the table. 
    */

    if (arguments.length === 0) {
      return this.#tableSummary;
    }
    else {
      const validString = (typeof inputSummary == typeof 'abc') && inputSummary;

      if (validString) {
        this.#tableSummary = inputSummary;
        return this;
      }
      else {
        console.error('tableSummary must be a non-empty string');
      }
    }
  }
  tableOrder(input) {
    /*
      the order property of data tables, array of arrays for each column.
      ex:
      input = [
        [0, 'asc'],
        [1, 'asc']
        
      ]
      based on https://datatables.net/reference/option/order
    */
    if (arguments.length === 0) {
      return this.#tableOrder;
    }
    else {
      this.#tableOrder = input;
      return this;
    }
  }

  // NO VALIDATION chaining methods (read: bugs are your responsibility)
  axisGens(inputAxes) {
    /*
    Parameters 
    ----------------
    inputAxes (type: array)
      - An array with two d3.axis generator functions.
      - The first is the category axis. The second as the numerical axis
    */
    if (arguments.length === 0) {
      return this.#axisGens;
    }
    else {
      this.#axisGens = { c: inputAxes[0], n: inputAxes[1] };
      return this;
    }
  }
  stackGen(inputStackGen) {
    /*
    Parameters 
    ----------------
    inputStackGen (type: function)
      - An d3.stack generator function.
    */
    if (arguments.length === 0) {
      return this.#stackGen;
    }
    else {
      this.#stackGen = inputStackGen;
      return this;
    }
  }
  stackData(inputStackData) {
    /*
    Parameters 
    ----------------
    inputStackData (type: array)
      - The return array of objects from calling a d3.stack 
        generator function.
    */
    if (arguments.length === 0) {
      return this.#stackData;
    }
    else {
      this.#stackData = inputStackData;
      return this;
    }
  }
  cScales(inputCScale) {
    /*
    Parameters 
    ----------------
    inputCScale (type: function)
      - A d3.scale function that will be used to space the labels and 
        categorical position of bars.
    */
    if (arguments.length === 0) {
      return this.#cScales;
    }
    else {
      this.#cScales = inputCScale;
      return this;
    }
  }
  nScale(inputNScale) {
    /*
    Parameters 
    ----------------
    inputNScale (type: function)
      - A d3.scale function that will be used to set the height of the bars
    */
    if (arguments.length === 0) {
      return this.#nScale;
    }
    else {
      this.#nScale = inputNScale;
      return this;
    }
  }
  cSubScale(inputCSubScale) {
    /*
    Parameters 
    ----------------
    inputCSubScale (type: function)
      - A d3.scale function that will be used to space the labels and 
        categorical position of bars for the subgroups in a grouped bar chart.
    */
    if (arguments.length === 0) {
      return this.#cSubScale;
    }
    else {
      this.#cSubScale = inputCSubScale;
      return this;
    }
  }
  colourScale(inputColourScale) {
    /*
    Parameters 
    ----------------
    inputColourScale (type: function)
      - A d3.scaleOrdinal function that will be used to colour the bars.
    */
    if (arguments.length === 0) {
      return this.#colourScale;
    }
    else {
      this.#colourScale = inputColourScale;
      return this;
    }
  }
  noCategoryColourScale(inputColourScale) {
    /*
    Parameters 
    ----------------
    inputColourScale (type: function)
      - A d3.scaleOrdinal function that will be used to colour the bars.
    */
    if (arguments.length === 0) {
      return this.#noCategoryColourScale;
    }
    else {
      this.#noCategoryColourScale = inputColourScale;
      return this;
    }
  }
  htmlLegend(input) {
    /*
    Parameters 
    ----------------
    inputContainer (type: D3.js selection)
      - A SVG DOM element to render the html legend in 
        (inputted as a d3.js selection)
    */
    if (arguments.length === 0) {
      return this.#htmlLegend;
    }
    else {
      this.#htmlLegend = input;
      return this;
    }
  }
  container(inputContainer) {
    /*
    Parameters 
    ----------------
    inputContainer (type: D3.js selection)
      - A SVG DOM element to render the bar graph in 
        (inputted as a d3.js selection)
    */
    if (arguments.length === 0) {
      return this.#container;
    }
    else {
      this.#container = inputContainer;
      return this;
    }
  }
  wrapper(inputWrapper) {
    /*
    Parameters 
    ----------------
    inputWrapper (type: D3.js selection)
      - A div containing the container element to render the 
        tooltips in (inputted as a d3.js selection)
    */
    if (arguments.length === 0) {
      return this.#wrapper;
    }
    else {
      this.#wrapper = inputWrapper;
      return this;
    }
  }
  barGroup(input) {
    if (arguments.length === 0) {
      return this.#barGroup;
    }
    else {
      this.#barGroup = input;
      return this;
    }
  }
  legendGroup(input) {
    if (arguments.length === 0) {
      return this.#legendGroup;
    }
    else {
      this.#legendGroup = input;
      return this;
    }
  }
  customGroup(input) {
    if (arguments.length === 0) {
      return this.#customGroup;
    }
    else {
      this.#customGroup = input;
      return this;
    }
  }
  axesGroup(input) {
    if (arguments.length === 0) {
      return this.#axesGroup;
    }
    else {
      this.#axesGroup = input;
      return this;
    }
  }
  titleGroup(input) {
    if (arguments.length === 0) {
      return this.#titleGroup;
    }
    else {
      this.#titleGroup = input;
      return this;
    }
  }
  table(inputTable) {
    /*
    Parameters 
    ----------------
    inputWrapper (type: D3.js selection)
      - A div to append the table to.
    */
    if (arguments.length === 0) {
      return this.#table;
    }
    else {
      this.#table = inputTable;
      return this;
    }
  }
  figureAriaLabel(input) {
    if (arguments.length === 0) {
      return this.#figureAriaLabel;
    }
    else {
      const validString = (typeof input == typeof 'abc') && input;

      if (validString) {
        this.#figureAriaLabel = input
        return this;
      }
      else {
        console.error('figureAriaLabel must be a non-empty string');
      }
    }
  }
  figureAriaDescription(input) {
    if (arguments.length === 0) {
      return this.#figureAriaDescription;
    }
    else {
      const validString = (typeof input == typeof 'abc') && input;

      if (validString) {
        this.#figureAriaDescription = input
        return this;
      }
      else {
        console.error('figureAriaDescription must be a non-empty string');
      }
    }
  }

  averageLines(input) {
    if (arguments.length === 0) {
      return this.#averageLines;
    }
    else {
      this.#averageLines = input
      return this;
    }
  }
  averageLinesColours(input) {
    if (arguments.length === 0) {
      return this.#averageLinesColours;
    }
    else {
      this.#averageLinesColours = input
      return this;
    }
  }
  averageLinesType(input) {
    if (arguments.length === 0) {
      return this.#averageLinesType;
    }
    else {
      this.#averageLinesType = input
      return this;
    }
  }
  averageLinesLegendText(input) {
    if (arguments.length === 0) {
      return this.#averageLinesLegendText;
    }
    else {
      this.#averageLinesLegendText = input
      return this;
    }
  }


  callbackClick(input) {
    if (arguments.length === 0) {
      return this.#callbackClick;
    }
    else {
      this.#callbackClick = input
      return this;
    }
  }
  callbackHover(input) {
    if (arguments.length === 0) {
      return this.#callbackHover;
    }
    else {
      this.#callbackHover = input
      return this;
    }
  }
  callbackLegendHover(input) {
    if (arguments.length === 0) {
      return this.#callbackLegendHover;
    }
    else {
      this.#callbackLegendHover = input
      return this;
    }
  }

  tableHeaderFunction(input) {
    if (arguments.length === 0) {
      return this.#tableHeaderFunction;
    }
    else {
      this.#tableHeaderFunction = input
      return this;
    }
  }
  tableCellFunction(input) {
    if (arguments.length === 0) {
      return this.#tableCellFunction;
    }
    else {
      this.#tableCellFunction = input
      return this;
    }
  }
  nTickFormat(input) {
    if (arguments.length === 0) {
      return this.#nTickFormat;
    }
    else {
      this.#nTickFormat = input;
      return this;
    }
  }
  cTickFormat(input) {
    if (arguments.length === 0) {
      return this.#cTickFormat;
    }
    else {
      this.#cTickFormat = input;
      return this;
    }
  }
  labelFormat(input) {
    if (arguments.length === 0) {
      return this.#labelFormat;
    }
    else {
      this.#labelFormat = input;
      return this;
    }
  }
  tooltipFunction(input) {
    if (arguments.length === 0) {
      return this.#tooltipFunction;
    }
    else {
      this.#tooltipFunction = input
      return this;
    }
  }
  hasRendered(input) {
    if (arguments.length === 0) {
      return this.#hasRendered;
    }
    else {
      this.#hasRendered = input
      return this;
    }
  }
  //#endregion

  //#region =============== HELPER METHODS (PUBLIC) ===================
  initContainer() {
    /*
    Assigns the basic attributes to the container svg.
    
    Parameters
    ----------------
    undefined
    - Note: Requires height and width to have a value

    Returns
    ----------------
    undefined
    
    */

    this.#container
      // .attr('height', this.#height)
      .attr('width', '100%')
      .attr('viewBox', `0 0 ${this.#width} ${this.#height}`)
      .attr("perserveAspectRatio", "xMinyMin meet")
      .attr('aria-label', this.#figureAriaLabel)
      .attr('aria-description', this.#figureAriaDescription)
      .attr('tabindex', 0)
  }
  initCategories() {
    let categories = [];
    this.#data.map(el => {
      let cat = el[this.#categoryKey];
      if (!categories.includes(cat)) {
        categories.push(cat)
      }
    })
    this.#categoryLookup = {};
    this.#categoryReverseLookup = {};

    categories.map((el, i) => {
      this.#categoryLookup[el] = "val" + i;
      this.#categoryReverseLookup["val" + i] = el;
    })
    this.#categories = categories;
  }
  initData(categories = this.#categories) {
    /* 
    This function initialises a d3.stack() function and its return data. 
    
    Parameters
    ----------------
    undefined
    - Though note that the scales will be initialised using
      the values of #ySeries, and #data.

    Returns
    ----------------
    undefined
    
    */


    this.#cKeys = this.#createCKeys(); // data

    // Create stack first (data needed for yScale)
    this.#stackGen = this.#createStackGen();

    let dataMaps = this.#cSeries.map(fv => function(d) { return d[fv] });
    this.#groupData = d3.rollups(this.#data, v => v, ...dataMaps);

    //make the data stacked
    if (!this.#grouped) {
      let createStackRow = (el) => {
        let rowCategories = []
        let stackRow = { ...el[1][0] }
        delete stackRow[this.#nKey]
        delete stackRow[this.#categoryKey]
        
        el[1].map(el => {
          rowCategories.push(el[this.#categoryKey])
          stackRow[el[this.#categoryKey]] = el[this.#nKey]
        })
        if (this.#proportional) {
          let total = 0;

          categories.map(n => {
            total += +stackRow[n]
          })
          categories.map(n => {
            stackRow[n] = stackRow[n] / total * 100.0
          })
          stackRow["total"] = total;
        }
        
        // console.log(el[1])
        // console.log('row', stackRow)
        // console.log(categories)
        // console.log(rowCategories)
        // el[1] = d3.stack().keys(categories)([stackRow])
        el[1] = d3.stack().keys(rowCategories)([stackRow])
      }
      
      this.#stackData = structuredClone(this.#groupData);

      let levels = [];
      this.#cSeries.map((c, i) => {
        let row = []
        if (i == 0) {
          if (i == this.#cSeries.length - 1) {
            this.#stackData.map(el => createStackRow(el))
          }
          row = this.#stackData.map(el => el)
        }
        else {
          levels[i - 1].map(el => {
            el[1].map(el => {
              if (i == this.#cSeries.length - 1) {
                createStackRow(el)
              }
              row.push(el)
            })
          })
        }
        levels[i] = row;
      })
      // console.log('levels', levels)
      
      if (this.#proportional) {
        this.#proportionalStack = this.#stackData
      }
    }
  }
  initcScales() {
    this.#surKeys = []
    this.#cScales = []

    // if (this.#surGroups.length != 0){
    this.#cSeries.map((group, i) => {

      //get unique keys from group
      let keys = []
      this.#data.map(el => {
        if (!keys.includes(el[group])) {
          keys.push(el[group])
        }
      })
      this.#surKeys.push(keys)

      //create cScales
      let scale;
      if (i == 0) {
        scale = d3
          .scaleBand()
          .domain(this.#surKeys[i])
          .range([this.#margins.l, this.#width - this.#margins.r])
          .padding([this.#cPaddingSeries ? this.#cPaddingSeries[i] : this.#defaultPadding]);

        // Adjust for horizontal bar graphs
        if (!this.#vertical) {
          scale = scale
            .range([this.#margins.t, this.#height - this.#margins.b]);
        }
      }
      else {
        scale = d3
          .scaleBand()
          .domain(this.#surKeys[i])
          .range([0, this.#cScales[i - 1].bandwidth()])
          .padding([this.#cPaddingSeries ? this.#cPaddingSeries[i] : this.#defaultPadding])
      }

      this.#cScales.push(scale);
    })
    // }
    // console.log("surKeys", this.#surKeys)
    // console.log("scales", this.#cScales)
  }
  initNScale(log = false, dataUpdate = true) {
    /*
      This function initialises a d3.scale function to set bar height.
      
      NOTE: Ensure that this.#stackGen and this.#stackData are set
      before calling this method.
    
      Parameters 
      -----------------
      log (type: bool)
        - Whether to set the bar height with a log scale.
    */

    let [min, max] = this.#dataMinMax(dataUpdate);
    this.#min = min;
    this.#max = max;
    // console.log('min', min, 'max', max)

    if (isNaN(min)) {
      this.#min = 0;
      min = 0;
    }
    if (isNaN(max)) {
      this.#max = 1;
      max = 1;
    }

    // Create log/lin functions
    if (log && this.#grouped) {
      this.#nScale = d3
        .scaleLog()
        // .domain([min > this.#logMin ? min : this.#logMin, max])
        .domain([min, max])
        .range([(this.#height - this.#margins.b), this.#margins.t]);
    }
    else if (this.#proportional && !this.#grouped) {
      this.#nScale = d3
        .scaleLinear()
        .domain([0, 100])
        .range([(this.#height - this.#margins.b), this.#margins.t]);
    }
    else {
      this.#nScale = d3
        .scaleLinear()
        .domain([0, max])
        .range([(this.#height - this.#margins.b), this.#margins.t]);
    }

    // Adjust for horizontal bar graphs
    if (!this.#vertical) {
      if (log && this.#grouped) {
        this.#nScale = this.#nScale
          .range([this.#margins.l, this.#width - this.#margins.l - this.#margins.r]);
      }
      else {
        this.#nScale = this.#nScale
          .range([this.#margins.l, this.#width - this.#margins.r]);
      }
    }

    if (this.#nAxisNice) {
      this.#nScale.nice();
    }

  }
  initCSubScale() {
    /* 
    Initialises a bandscale for the categorical axis
    
    Parameters
    -------------------
    undefined
    - Though note that this method relies on values of #data, #cSeries, #categories, #cScale,
      #margins, #subPadding, and #width. Please initialise those before calling the method
      
    Returns
    -------------------
    undefined
    */

    this.#cSubScale = d3
      .scaleBand()
      .domain(this.#categories)
      .range([0, this.#cScales[this.#cScales.length - 1].bandwidth()])
      .padding([this.#subPadding ?? this.#defaultPadding]);
  }
  initColourScale() {
    /*
    Initializes a scaleOrdinal for the colours of the bars.
    */
    this.#colourScale = d3
      .scaleOrdinal()
      .domain(this.#categories)
      .range(this.#colourSeries)
  }
  initTextures() {
    let gridTexture = (stroke, background) => {
      let t = textures.lines()
        .orientation("vertical", "horizontal")
        .size(4)
        .strokeWidth(0.5)
        .shapeRendering("crispEdges")
        .stroke(stroke)
        .background(background);
      this.#container.call(t)
      return t;
    }
    let dotsTexture = (stroke, background) => {
      let t = textures.circles()
        .complement()
        .thicker()
        .radius(1)
        .stroke(stroke)
        .background(background);
      this.#container.call(t)
      return t;
    }
    let diagonalTexture = (stroke, background) => {
      let t = textures.lines()
        .orientation("diagonal")
        .size(10)
        .strokeWidth(1)
        .stroke(stroke)
        .background(background);
      this.#container.call(t)
      return t;
    }

    this.#categories.map((cat, index) => {
      let stroke = 'black'
      let myColour = this.#colourScale(cat)
      let chosenTexture = this.#textureTypeSeries[index % this.#textureTypeSeries.length]

      let t;
      if (chosenTexture == 'solid') {
        t = 'solid';
      }
      else if (chosenTexture == "grid") {
        t = gridTexture(stroke, myColour)
      }
      else if (chosenTexture == "dots") {
        t = dotsTexture(stroke, myColour)
      }
      else if (chosenTexture == "diagonal") {
        t = diagonalTexture(stroke, myColour)
      }

      this.#textureSeries.push(t)
    })

    // console.log(this.#textureSeries)

    // this.#container.call(t);
  }
  initAxes() { //cAxisOptions = {}, nAxisOptions = {}
    /*
    This function initialises the bottom and left scales for the bar graph
    
    Parameters
    -----------------
    cAxisOptions/nAxisOptions (type: object)
    - Objects with settings to configure the categorical and numerical axes. 
    - Input settings as key-value pairs in the objects. 
    - Valid keys are `ticks`, `tickValues`, `tickFormat`, `tickPadding`, and
      `tickSize`.
    - See d3.js documentation for valid values;
    - Also note that this function relies on #cScale and #nScale. 
      Make sure these are initialised.
      
    Returns
    -----------------
    undefined
    */

    //axes options
    let nAxisOptions = {};
    let cAxisOptions = {};

    if (this.#nAxisTickNumber) {
      nAxisOptions['ticks'] = this.#nAxisTickNumber;
    }
    if (this.#gridlines) {
      const gridHeight = this.#height - this.#margins.b - this.#margins.t;
      const gridWidth = this.#width - this.#margins.l - this.#margins.r;
      const gridlineLength = this.#vertical ? -gridWidth : -gridHeight;

      nAxisOptions["tickSizeInner"] = gridlineLength
      nAxisOptions["tickPadding"] = 10
    }
    if (this.#proportional && !this.#grouped && !this.#nTickFormat) {
      nAxisOptions["tickFormat"] = d => d + '%';
    }
    if (this.#nTickFormat) {
      nAxisOptions["tickFormat"] = this.#nTickFormat;
    }
    if (this.#cTickFormat) {
      cAxisOptions["tickFormat"] = this.#cTickFormat;
    }

    // Create axes
    let n = this.#vertical ? d3.axisLeft(this.#nScale) : d3.axisBottom(this.#nScale);
    let c = [];

    this.#cScales.map(scale => {
      c.push(this.#vertical ? d3.axisBottom(scale) : d3.axisLeft(scale));
    })

    // if (!this.#vertical) {
    //   n = d3.axisBottom(this.#nScale);
    //   c = d3.axisLeft(this.#cScales[0]);
    // }

    // Set options
    function setOptions(ax, obj) {
      if (obj.ticks) ax.ticks(obj.ticks);
      if (obj.tickValues) ax.tickValues(obj.tickValues);
      if (obj.tickFormat) ax.tickFormat(obj.tickFormat);
      if (obj.tickPadding) ax.tickPadding(obj.tickPadding);
      if (obj.tickSizeOuter) ax.tickSizeOuter(obj.tickSizeOuter);
      if (obj.tickSizeInner) ax.tickSizeInner(obj.tickSizeInner);
    }

    setOptions(n, nAxisOptions);
    // console.log(c)
    c.map(c => {
      setOptions(c, cAxisOptions);
    })


    this.#axisGens = { c, n };
  }
  initBarWidth() {
    /*
    Computes width of each bar
    
    Parameters
    ---------------
    undefined
    - Though note that this method relies on #margins, #width, 
      #data, #grouped, and #padding. Initialise those as you'd like first
      
    Returns
    ---------------
    undefined
    */

    if (this.#grouped) {
      this.#barWidth = this.#cSubScale.bandwidth()
    }
    else {
      this.#barWidth = this.#cScales[this.#cScales.length - 1].bandwidth()
    }

  }
  init() {
    /* 
    This is a generic method that calls all the above methods
    with default parameters. Ie. It initialises a default cScale, nScale,
    stack, barWidth, cAxis, and nAxis. 
    
    Feel free to call this and then some of the more specific methods above
    to adjust a certain variable (ex: the axes only or the cScale only)
    
    Parameters: 
    -------------------
    undefined
    
    Returns:
    -------------------
    undefined
    */
    this.initContainer();
    this.initCategories();
    this.initData();
    this.initcScales();
    // console.log(this.#surKeys)
    // console.log(this.#cScales)
    this.initNScale(this.#log);
    // this.initCScale();
    this.initCSubScale();
    this.initColourScale();
    if (this.#textures) {
      this.initTextures();
    }

    this.initAxes();
    this.initBarWidth();

    return this;
  }
  clear() {
    /* 
    Clears all contents of the SVG container, wrapper
    */

    this.#wrapper
      .select('div.tooltip')
      .remove();
    this.#container
      .selectAll("*")
      .remove();

    return this;
  }
  render() {
    // Render tooltips
    let tooltipEnter, tooltipLeave, tooltipMove;
    if (this.#tooltips) {
      [tooltipEnter, tooltipLeave, tooltipMove] = this.#renderTooltips();
    }
    if (this.#gridlines) {
      // Render axes
      this.#renderAxes();
      // Render bars
      this.#renderBars(tooltipEnter, tooltipLeave, tooltipMove);
    }
    else {
      // Render bars
      this.#renderBars(tooltipEnter, tooltipLeave, tooltipMove);
      // Render axes
      this.#renderAxes();
    }

    //Render average lines
    if (this.#averageLines) {
      this.#renderAverageLines();
    }


    // Render legends
    this.#renderLegend();

    if (this.#addCustomGroup) {
      this.#renderCustomGroup();
    }

    if (this.#averageLines) {
      this.#renderAverageLinesLegend();
    }

    if (this.#barHoverFade) {
      this.#addBarHoverFade();
    }
    if (this.#legendHoverFade) {
      this.#addLegendHoverFade();
    }

    // Render chart titles
    this.#renderTitles();


    // if (this.#interactive) {
    this.#addInteraction();
    // }

    this.#setTabbing();

    if (this.#table) {
      this.#addTable();
    }

    this.#hasRendered = true;

    return this;
  }
  update() {
    // Update tooltips
    let tooltipEnter, tooltipLeave, tooltipMove;
    if (this.#tooltips) {
      [tooltipEnter, tooltipLeave, tooltipMove] = this.#renderTooltips();
    }

    this.#updateAxes();
    // Update bars
    this.#renderBars(tooltipEnter, tooltipLeave, tooltipMove);

    this.#renderLegend();

    if (this.#averageLines) {
      this.#renderAverageLinesLegend();
    }

    if (this.#barHoverFade) {
      this.#addBarHoverFade();
    }
    if (this.#legendHoverFade) {
      this.#addLegendHoverFade();
    }

    // update chart titles
    this.#renderTitles();

    // if (this.#interactive) {
    this.#addInteraction();
    // }

    if (this.#table) {
      this.#addTable();
    }

    return this;
  }
  magic() {
    this.init()

    this.#hasRendered ? this.update() : this.render()

    return this
  }
  //#endregion

  //#region =============== HELPER METHODS (PRIVATE) ===================
  #createCKeys(data = this.#data) {
    let cKeys = [];
    data.map(el => {
      if (!cKeys.includes(el[this.#cSeries]))
        cKeys.push(el[this.#cSeries])
    })
    return cKeys;
  }
  #createStackGen(categories = this.#categories) {
    return d3.stack().keys(categories);
  }
  #createProportionalStackData(data = this.#data, categories = this.#categories, stackGen = this.#stackGen) {
    let sData = stackGen(data)
    // console.log(sData)
    sData.map(el => {
      el.map(d => {
        let total = 0
        categories.map(n => {
          total += +d.data[n]
        })
        d["total"] = total;
        d[0] = Math.round(d[0] / total * 100)
        d[1] = Math.round(d[1] / total * 100)
      })
    });
    return sData;
  }
  #rebaseStackData(stackData = this.#stackData, cKeys = this.#cKeys) {
    let newStackData = cKeys.map((ckey, i) => {
      let newRow = []
      stackData.map((el, k) => {
        let newArr = el[i]
        newArr["key"] = el.key
        newRow.push(newArr)
      })
      newRow["key"] = ckey;
      return newRow;
    })
    return newStackData;
  }
  #getCssProperty(element, property) {
    return window.getComputedStyle(element, null).getPropertyValue(property);
  }
  #getFullFont(element) {
    let fontWeight = this.#getCssProperty(element, 'font-weight') || 'normal';
    let fontSize = this.#getCssProperty(element, 'font-size') || '16px';
    let fontFamily = this.#getCssProperty(element, 'font-family') || '"Noto Sans",sans-serif';
    return `${fontWeight} ${fontSize} ${fontFamily}`;
  }
  #calculateTextDimensions(text, font) {
    let canvas = this.#calculateTextDimensions.canvas || (this.#calculateTextDimensions.canvas = document.createElement("canvas"));
    let context = canvas.getContext("2d");
    context.font = font;
    let metrics = context.measureText(text);
    // console.log('metrics', metrics)
    let width = metrics.width;
    let height = metrics.fontBoundingBoxAscent;
    return { width, height };
  }
  #labelFitsStackedBar(textWidth, textHeight, nScale, d) {
    if (this.#alwaysDisplayBarLabels)
      return true;
    let xVal = this.#vertical ? textWidth : textHeight;
    let yVal = this.#vertical ? textHeight : textWidth;
    let rectY = Math.abs(nScale(d[0]) - nScale(d[1]))

    // console.log(xVal, this.#barWidth)

    //does the text fit in the rect?
    return yVal <= rectY && xVal <= this.#barWidth;
  }
  #labelFitsGroupedBar(textWidth, textHeight, d) {
    if (this.#alwaysDisplayBarLabels)
      return true;
    let xVal = this.#vertical ? textWidth : textHeight;
    let paddedWidth = this.#cSubScale.step()

    // console.log(xVal, this.#barWidth)

    return xVal <= paddedWidth;

  }
  #round(number) {
    if (!isNaN(this.#decimalPlaces)) {
      let multiplier = Math.pow(10, this.#decimalPlaces)
      return Math.round(number * multiplier) / multiplier
    }
    else {
      return number;
    }
  }
  #getLabel(value, isProportionalLabel = true) {
    let newValue;

    if (this.#labelFormat) {
      return this.#labelFormat(value)
    }
    newValue = this.#round(value)
    if (this.#decimalType == "fixed") {
      newValue = newValue.toFixed(this.#decimalPlaces)
    }
    // console.log(value)
    if (isNaN(newValue)) {
      return value;
    }
    return newValue + ((isProportionalLabel || this.#percent) ? '%' : '');
  }
  #calcGroupedXPos(d) {
    // console.log(d)
    let xPos = 0;

    this.#cSeries.map((c, i) => {
      xPos += this.#cScales[i](d[c])
      // console.log(this.#cScales)
      // console.log(d.data[c])
    })
    // console.log(xPos)
    return xPos;
  }
  #uncertaintyIsNaN(d) {
    return isNaN(d[this.#upperUncertainty]) || isNaN(d[this.#lowerUncertainty]);
  }
  #updateUncertaintyLine(selection, key, verticalLine = true) {
    let y1 = this.#vertical ? 'y1' : 'x1';
    let y2 = this.#vertical ? 'y2' : 'x2';
    let x1 = this.#vertical ? 'x1' : 'y1';
    let x2 = this.#vertical ? 'x2' : 'y2';

    selection
      .transition()
      .duration(this.#transitionDuration)
      .attr(y1, d => {
        if (this.#uncertaintyIsNaN(d)) {
          return this.#nScale(0)
        }
        return verticalLine ? this.#nScale(d[this.#lowerUncertainty]) : this.#nScale(d[key]);
      })
      .attr(y2, d => {
        if (this.#uncertaintyIsNaN(d)) {
          return this.#nScale(0)
        }
        return verticalLine ? this.#nScale(d[this.#upperUncertainty]) : this.#nScale(d[key])
      })
      .attr(x1, d => verticalLine ? this.#cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + this.#cSubScale.bandwidth() / 2 : this.#cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) - this.#uncertaintyWidth / 2 + this.#cSubScale.bandwidth() / 2)
      .attr(x2, d => verticalLine ? this.#cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + this.#cSubScale.bandwidth() / 2 : this.#cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + this.#uncertaintyWidth / 2 + this.#cSubScale.bandwidth() / 2)
      .attr('opacity', d => this.#uncertaintyIsNaN(d) ? 0 : 1)
  }
  #updateUncertaintyLineRemove(selection, key, verticalLine = true) {
    let y1 = this.#vertical ? 'y1' : 'x1';
    let y2 = this.#vertical ? 'y2' : 'x2';
    // let x1 = this.#vertical ? 'x1' : 'y1';
    // let x2 = this.#vertical ? 'x2' : 'y2';

    selection
      .transition()
      .duration(this.#transitionDuration)
      .attr(y1, d => this.#nScale(0))
      .attr(y2, d => this.#nScale(0))
      .attr('opacity', 0)
  }
  #renderCustomGroup() {
    if (!this.#customGroup)
      this.#customGroup = this.#container.append('g').attr('class', 'custom')
  }
  #barLabelTweenStacked(selection, d) {
    let that = this;
    let oldVal = selection.attr('data-raw-value') //selection.text().replace('%', '');

    let newVal = d[0][1] - d[0][0];
    if (isNaN(newVal)) {
      newVal = d[0].data[d.key]
    }

    let label = this.#getLabel(newVal, this.#proportional);

    if (!isNaN(newVal) && !isNaN(oldVal)) {
      const i = d3.interpolate(+oldVal, newVal);
      return function(t) {
        selection.text(that.#getLabel(i(t), that.#proportional));
      };
    }
    else {
      selection.text(label)
    }
  }
  #barLabelTweenGrouped(selection, d) {
    let that = this;
    let oldVal = selection.attr('data-raw-value') //selection.text().replace('%', '');

    let newVal = d[this.#nKey];
    // if (isNaN(newVal)){
    //   newVal = d[0].data[d.key]
    // }

    let label = this.#getLabel(newVal, this.#proportional);

    if (!isNaN(newVal) && !isNaN(oldVal)) {
      const i = d3.interpolate(+oldVal, newVal);
      return function(t) {
        selection.text(that.#getLabel(i(t), that.#proportional));
      };
    }
    else {
      selection.text(label)
    }
  }
  #renderBars(tooltipEnter, tooltipLeave, tooltipMove) {
    if (!this.#barGroup)
      this.#barGroup = this.#container.append('g').attr('class', 'bars')

    let bars = this.#barGroup

    // Save private fields (can't access 'this' when rendering bars)
    const that = this;
    const cSeriesLast = this.#cSeries[this.#cSeries.length - 1];
    const cSeries = this.#cSeries
    const categories = this.#categories;
    const nScale = this.#nScale;
    const cScales = this.#cScales;
    const cScale = this.#cScales[this.#cScales.length - 1];
    const cSubScale = this.#cSubScale;
    const barWidth = this.#barWidth;
    const graphWidth = this.#width;
    const barLabels = this.#barLabels;
    const colourScale = this.#colourScale;
    const loadAnimation = this.#loadAnimation; // this doesn't do anything right now
    const proportional = this.#proportional;
    const grouped = this.#grouped;

    // console.log("cScales", cScales);


    const categoryLookup = this.#categoryLookup;
    const categoryReverseLookup = this.#categoryReverseLookup;

    // Vertical / horizontal adjustment
    const vertical = this.#vertical;
    const x = vertical ? 'x' : 'y';
    const y = vertical ? 'y' : 'x';
    const h = vertical ? 'height' : 'width';
    const w = vertical ? 'width' : 'height';
    const verticalTextAnchor = vertical ? 'middle' : 'start';

    // Create subgroups for each bar series
    const first = this.#vertical ? 0 : 1;
    const last = this.#vertical ? 1 : 0;

    const lightFontColour = "white"
    const darkFontColour = "black";



    //colour checkers to determine font color for stacked barcharts
    //https://www.w3.org/TR/2008/REC-WCAG20-20081211/
    const contrastRatio = 4.5;

    let checkContrastToWhite = (hexColour) => {
      return contrastToWhite(hexColour) > contrastRatio;
    };

    let contrastToWhite = (hexColour) => {
      let whiteIlluminance = 1;
      let illuminance = calculateIlluminance(hexColour);
      return whiteIlluminance / illuminance;
    };

    let hex2Rgb = (hexColour) => {
      let result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hexColour);
      if (result) {
        //breakdown the matched hexColour
        return {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16)
        }
      }
      else {
        //assume it is rgb, so break it down
        let [r, g, b] = hexColour.match(/\d+/g).map(Number)
        return {
          r: r,
          g: g,
          b: b
        }
      }
    };

    //relative contrast coefficients, relative luminance section of above doc
    const rCC = 0.2126; //red
    const gCC = 0.7152; //green
    const bCC = 0.0722; //blue
    const gamma = 2.4;

    let calculateIlluminance = (hexColour) => {
      let rgbColour = hex2Rgb(hexColour);
      let r = rgbColour.r,
        g = rgbColour.g,
        b = rgbColour.b;
      let a = [r, g, b].map(function(v) {
        v /= 255;
        return (v <= 0.03928) ?
          v / 12.92 :
          Math.pow(((v + 0.055) / 1.055), gamma);
      });
      return a[0] * rCC + a[1] * gCC + a[2] * bCC;
    };


    //log of 0 does not exist, cannot have 0 on a log scale
    let lowestNValue = this.#grouped && this.#log ? this.#min : 0;

    //used for mono category charts (only one grouping in legend)
    let rectCount = 0;

    let createUncertaintyLine = (selection, id, key, verticalLine = true) => {
      let y1 = this.#vertical ? 'y1' : 'x1';
      let y2 = this.#vertical ? 'y2' : 'x2';
      let x1 = this.#vertical ? 'x1' : 'y1';
      let x2 = this.#vertical ? 'x2' : 'y2';

      // console.log()

      selection.append('line')
        // .attr('class', 'uncertainty')
        .attr('data-uncertainty', id)
        // .attr("fill", 'black')
        .attr("stroke", 'black')
        .attr(y1, d => {
          if (this.#uncertaintyIsNaN(d)) {
            return this.#nScale(0)
          }
          return verticalLine ? this.#nScale(d[this.#lowerUncertainty]) : this.#nScale(d[key])
        })
        .attr(y2, d => {
          if (this.#uncertaintyIsNaN(d)) {
            return this.#nScale(0)
          }
          return verticalLine ? this.#nScale(d[this.#upperUncertainty]) : this.#nScale(d[key])
        })
        .attr(x1, d => verticalLine ? cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + barWidth / 2 : cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) - this.#uncertaintyWidth / 2 + barWidth / 2)
        .attr(x2, d => verticalLine ? cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + barWidth / 2 : cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + this.#uncertaintyWidth / 2 + barWidth / 2)
        .attr('opacity', 0)
        .transition()
        .duration(this.#transitionDuration)
        .attr('opacity', d => this.#uncertaintyIsNaN(d) ? 0 : 1)

    }

    let determineRectFill = (d, i, key) => {
      let myColour;
      if (this.#categories.length > 1) {
        myColour = colourScale(key)
      }
      else {
        if (this.#noCategoryColourScale) {
          myColour = this.#noCategoryColourScale(this.#grouped ? d[this.#cSeries[this.#cSeries.length - 1]] : d[0].data[this.#cSeries[this.#cSeries.length - 1]])
        }
        else {
          myColour = this.#colourSeries[rectCount++ % this.#colourSeries.length];
        }

      }
      if (this.#textures && this.#textureSeries[i] != 'solid') {
        return this.#textureSeries[i].url();
      }
      return myColour;
    }

    // for stacked bar graphs
    if (!this.#grouped) {
      // console.log("stackData", this.#stackData)
      let barGroups = bars
        .selectAll("g[data-layer='0']")
        .data(this.#stackData)
        // .data(this.#groupData)
        .join(
          (enter) => {
            let g = enter.append('g').attr('class', 'bar-group')
              .attr('aria-label', d => {
                // console.log(d)
                return d[0] // key
              })
              .attr('data-layer', 0)

            this.#cSeries.map((c, i) => {
              if (i != 0) {
                g = g
                  .selectAll('g')
                  .data(d => {
                    return d[1]
                  })
                  .join('g')

                g
                  .attr('class', 'bar-group')
                  .attr('aria-label', d => {
                    // console.log(d)
                    return d[0] // key
                  })
                  .attr('data-layer', i)
                  .attr('opacity', 1)
              }
            })

            let rect = g
              .selectAll('rect')
              .data(d => {
                // console.log(d)
                return d[1]
              })
              .join('rect')

            rect
              .attr(x, d => {
                // console.log(d)
                // return cScale(d.data[cSeries])
                return this.#calcGroupedXPos(d[0].data)
              })
              .attr(w, barWidth)
              .attr(y, d => nScale(lowestNValue))
              .attr('opacity', 0)
              .attr('class', d => categoryLookup[d.key])
              .attr('fill', (d, i) => {
                // let myColour;
                // if (this.#categories.length > 1) {
                //   myColour = colourScale(d.key)
                // }
                // else {
                //   myColour = this.#colourSeries[rectCount++ % this.#colourSeries.length];
                // }
                // if (this.#textures && this.#textureSeries[i] != 'solid') {
                //   return this.#textureSeries[i].url();
                // }
                // return myColour
                return determineRectFill(d, i, d.key)
              })
              .transition()
              .duration(this.#transitionDuration)
              .attr(y, d => {
                let yVal = d[0][last];
                const input = isNaN(yVal) ? 0 : yVal;
                // console.log(yVal);
                return nScale(input);
              })
              .attr(h, d => {
                let height = nScale(d[0][first]) - nScale(d[0][last])
                return height == 0 || isNaN(height) ? 0.1 : height
              })
              .attr('opacity', 1)


            rect
              .attr('aria-label', d => {
                // console.log(d)
                if (d.key) {
                  return `${d.key}: ${this.#getLabel(d[0][1] - d[0][0], proportional)}`
                }
                else {
                  return `${this.#getLabel(d[0][1] - d[0][0], proportional)}`
                }
              })
              .attr('tabindex', -1)

            rect
              .on('mouseenter', tooltipEnter)
              // .on('focus', (e, d) => {
              //   tooltipEnter(e, d)
              // })
              .on('mouseleave', tooltipLeave)
              // .on('focus.bar', tooltipLeave)
              .on('mousemove', tooltipMove);

            // if (this.#interactive) {
            rect.attr('cursor', this.#interactive ? 'pointer' : 'auto')
            // }

            // creates bar labels
            if (barLabels) {
              let text = g
                .selectAll('text')
                .data(d => {
                  // console.log(d)
                  return d[1]
                })
                .join('text')

              text
                .attr('class', d => {
                  return `bar-label ${categoryLookup[d.key]}-label`
                })
                .attr('data-raw-value', d => {
                  let val = d[0][1] - d[0][0]
                  if (isNaN(val)) {
                    return d[0].data[d.key];
                  }
                  else {
                    return val;
                  }
                })
                .attr('fill', d => {
                  return checkContrastToWhite(colourScale(d.key)) ? lightFontColour : darkFontColour;
                })
                .attr("alignment-baseline", 'middle')
                .attr('dominant-baseline', 'middle')
                .attr('text-anchor', 'middle')
                .on('mouseenter', tooltipEnter)
                .on('mouseleave', tooltipLeave)
                .on('mousemove', tooltipMove)
                .text(d => {
                  // console.log(d)
                  if (typeof d[0][last] == 'number' && d[0][1] - d[0][0] >= 0) {
                    return this.#getLabel(d[0][1] - d[0][0], proportional);
                  }
                  else {
                    //NaN values
                    return d[0].data[d.key]
                  }
                });
              text
                .attr('opacity', 0)
                .attr(x, d => {
                  // console.log(d)
                  // console.log(cScale(d.data[cSeries]))
                  // return cScale(d.data[cSeries]) + barWidth / 2
                  return this.#calcGroupedXPos(d[0].data) + barWidth / 2
                })
                .attr(y, d => nScale(lowestNValue))
                .transition()
                .duration(this.#transitionDuration)
                .attr(y, d => {
                  let avg = (d[0][first] + d[0][last]) / 2
                  // console.log(d)
                  if (avg != 0 && !isNaN(avg)) {
                    return nScale(avg)
                  }
                  else {
                    return nScale(lowestNValue)
                  }
                })
                .attr('opacity', function(d) {
                  let dimensions = that.#calculateTextDimensions(that.#getLabel(d[0][1] - d[0][0], proportional), that.#getFullFont(this))
                  return that.#labelFitsStackedBar(dimensions.width, dimensions.height, nScale, d[0]) ? 1 : 0;
                })
                .on('end', function(d) {
                  let selection = d3.select(this);
                  selection.attr('display', function(d) {
                    let dimensions = that.#calculateTextDimensions(that.#getLabel(d[0][1] - d[0][0], proportional), that.#getFullFont(this))
                    return that.#labelFitsStackedBar(dimensions.width, dimensions.height, nScale, d[0]) ? 'block' : 'none';
                  })
                })

            }
          },
          (update) => {
            // console.log('updateStacked', update)
            // console.log('updatRect', update.selectAll('rect'))
            let g = update
              .attr('class', 'bar-group')
              .attr('aria-label', d => {
                // console.log(d)
                return d[0] // key
              })

            this.#cSeries.map((c, i) => {
              if (i != 0) {
                g
                  .selectAll(`g[data-layer='${i}']`)
                  .data(d => {
                    return d[1]
                  })
                  // .join('g')
                  .join(
                    enter => {
                      g = enter.append('g')
                        .attr('class', 'bar-group')
                        .attr('aria-label', d => {
                          // console.log(d)
                          return d[0] // key
                        })
                        .attr('data-layer', i)
                        .attr('opacity', 1)
                    },
                    update => {
                      // console.log('midg', update)
                      let newg = update
                        .attr('class', 'bar-group')
                        .attr('aria-label', d => {
                          // console.log(d)
                          return d[0] // key
                        })
                        .attr('data-layer', i)
                        .transition().duration(this.#transitionDuration)
                        .attr('opacity', 1)
                      g = g.merge(newg)
                    },
                    exit => {
                      //remove rectangles in removed groups to be removed
                      exit.selectAll('rect').transition().duration(this.#transitionDuration)
                        // .attr('opacity', 0)
                        .attr(h, 0)
                        .attr(y, nScale(lowestNValue))
                        .remove()

                      exit.selectAll('text').transition().duration(this.#transitionDuration)
                        .attr(y, nScale(lowestNValue))
                        .remove()

                      //remove groups
                      exit
                        .attr('opacity', 1)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)
                        .remove();
                    }
                  )

                // g
                //   .attr('class', 'bar-group')
                //   .attr('aria-label', d => {
                //     // console.log(d)
                //     return d[0] // key
                //   })
                //   .attr('data-layer', i)
              }
            })

            // console.log(g)

            let updateRect = selection => {
              selection
                .attr('aria-label', d => {
                  if (d.key) {
                    return `${d.key}: ${this.#getLabel(d[0][1] - d[0][0], proportional)}`
                  }
                  else {
                    return `${this.#getLabel(d[0][1] - d[0][0], proportional)}`
                  }
                })
                .attr(w, function(d) {
                  let value = d3.select(this).attr(w)
                  if (value === null)
                    return barWidth;
                  else
                    return value;
                })
                .attr('class', d => categoryLookup[d.key])
                .attr(x, function(d) {
                  let value = d3.select(this).attr(x)
                  if (value === null)
                    return that.#calcGroupedXPos(d[0].data)
                  else
                    return value;
                })
                .attr(y, function(d) {
                  let value = d3.select(this).attr(y)
                  if (value === null)
                    return nScale(lowestNValue);
                  else
                    return value;
                })
                .on('mouseenter', tooltipEnter)
                .on('mouseleave', tooltipLeave)
                .on('mousemove', tooltipMove)
                .transition()
                .duration(this.#transitionDuration)
                .attr(y, d => {
                  let yVal = d[0][last];
                  const input = isNaN(yVal) ? 0 : yVal;
                  // console.log(yVal);
                  return nScale(input);
                })
                .attr(h, d => {
                  let height = nScale(d[0][first]) - nScale(d[0][last])
                  return height == 0 || isNaN(height) ? 0.1 : height
                })
                .attr(x, d => {
                  // console.log(d)
                  // return cScale(d.data[cSeries])
                  return this.#calcGroupedXPos(d[0].data)
                })
                .attr(w, barWidth)
                // .attr('opacity', 1)
                .attr('fill', (d, i) => {
                  // let myColour;
                  // if (this.#categories.length > 1) {
                  //   myColour = colourScale(d.key)
                  // }
                  // else {
                  //   myColour = this.#colourSeries[rectCount++ % this.#colourSeries.length];
                  // }
                  // if (this.#textures && this.#textureSeries[i] != 'solid') {
                  //   return this.#textureSeries[i].url();
                  // }
                  // return myColour
                  return determineRectFill(d, i, d.key)
                })
                .attr('opacity', 1)

              // if (this.#interactive) {
              selection.attr('cursor', this.#interactive ? 'pointer' : 'auto')
              // }
            }

            let rect = g.selectAll('rect')
              .data(d => d[1])
              .join(
                (enter) => {
                  updateRect(enter.append('rect'))
                },
                (update) => {
                  updateRect(update)
                },
                (exit) => {
                  exit.transition().duration(this.#transitionDuration)
                    .attr('opacity', 0)
                    .attr(h, 0)
                    .attr(y, nScale(lowestNValue))
                    .remove()
                }
              )

            // // update bar labels
            if (barLabels) {

              let updateText = selection => {
                selection
                  .attr("alignment-baseline", 'middle')
                  .attr('dominant-baseline', 'middle')
                  .attr('text-anchor', 'middle')
                  //for new text that aren't in new groups, set default values before transition. Avoids transitioning from top left
                  .attr(x, function(d) {
                    let value = d3.select(this).attr(x)
                    if (value === null)
                      return that.#calcGroupedXPos(d[0].data) + barWidth / 2;
                    else
                      return value;
                  })
                  .attr(y, function(d) {
                    let value = d3.select(this).attr(y)
                    if (value === null || isNaN(value))
                      return nScale(0);
                    else
                      return value;
                  })
                  .attr('class', d => {
                    return `bar-label ${categoryLookup[d.key]}-label`
                  })
                  .attr('display', 'block')
                  .transition()
                  .duration(this.#transitionDuration)
                  .attr('fill', d => {
                    return checkContrastToWhite(colourScale(d.key)) ? lightFontColour : darkFontColour;
                  })
                  .attr(x, d => {
                    return this.#calcGroupedXPos(d[0].data) + barWidth / 2
                  })
                  .attr(y, d => {
                    let avg = (d[0][first] + d[0][last]) / 2
                    if (avg != 0 && !isNaN(avg)) {
                      return nScale(avg)
                    }
                    else {
                      return nScale(lowestNValue)
                    }
                  })
                  .attr('opacity', function(d) {
                    let dimensions = that.#calculateTextDimensions(that.#getLabel(d[0][1] - d[0][0], proportional), that.#getFullFont(this))
                    return that.#labelFitsStackedBar(dimensions.width, dimensions.height, nScale, d[0]) ? 1 : 0;
                  })
                  .tween("text", function(d) {
                    let selection = d3.select(this);
                    return that.#barLabelTweenStacked(selection, d)
                  })
                  .attr('data-raw-value', function(d) {
                    let selection = d3.select(this);
                    let val = d[0][1] - d[0][0];
                    if (!isNaN(val) && isNaN(selection.attr('data-raw-value'))) {
                      selection.attr('data-raw-value', 0)
                    }
                    else if (isNaN(val)) {
                      //if it's not a number, make it the raw value
                      return d[0].data[d.key]
                    }
                    // else {
                    return val
                    // }
                  })
                  .on('end', function(d) {
                    let selection = d3.select(this);
                    selection.attr('display', function(d) {
                      let dimensions = that.#calculateTextDimensions(that.#getLabel(d[0][1] - d[0][0], proportional), that.#getFullFont(this))
                      return that.#labelFitsStackedBar(dimensions.width, dimensions.height, nScale, d[0]) ? 'block' : 'none';
                    })
                  })


                selection
                  .on('mouseenter', tooltipEnter)
                  .on('mouseleave', tooltipLeave)
                  .on('mousemove', tooltipMove)
              }

              let text = g
                .selectAll('text')
                .data(d => d[1])
                // .join('text')
                .join(
                  (enter) => {
                    updateText(enter.append('text'))
                  },
                  (update) => {
                    updateText(update)
                  },
                  (exit) => {
                    exit
                      .transition()
                      .duration(this.#transitionDuration)
                      .attr('opacity', 0)
                      .attr(y, nScale(lowestNValue))
                      .remove()
                  }
                )
            }
          },
          (exit) => {
            exit.selectAll('*')
              .transition()
              .duration(this.#transitionDuration)
              .attr('opacity', 0)
              .attr(h, 0)
              .attr(y, nScale(lowestNValue))
              .remove()
            // .on('end', () => {
            //   exit.remove()
            // })
          })
    }

    // for grouped bar graphs
    else {
      // console.log("groupData", this.#groupData)
      bars
        // Create groups and update loops for data changes
        .selectAll("g[data-layer='0']")
        // .data(groupedData)
        .data(this.#groupData)
        .join(
          enter => {
            // let groups = []

            let g = enter.append('g').attr('class', 'bar-group')
              .attr('aria-label', d => {
                // console.log(d)
                return d[0] // key
              })
              .attr('data-layer', 0)
              .attr('tabindex', -1)

            this.#cSeries.map((c, i) => {
              if (i != 0) {
                g = g
                  .selectAll('g')
                  .data(d => {
                    return d[1]
                  })
                  .join('g')

                g
                  .attr('class', 'bar-group')
                  .attr('aria-label', d => {
                    // console.log(d)
                    return d[0] // key
                  })
                  .attr('data-layer', i)
                  .attr('opacity', 1)
                  .attr('tabindex', -1)
              }
            })

            let rect = g
              .selectAll('rect')
              .data(d => {
                // console.log(d[1]);
                return d[1]
              })
              .join('rect')

            rect
              .attr('tabindex', -1)
              .attr('aria-label', d => {
                if (this.#categoryKey) {
                  return `${d[this.#categoryKey]}: ${d[this.#nKey]}`
                }
                else {
                  return `${this.#getLabel(d[this.#nKey], proportional)}`
                }
              })
              .attr('opacity', 1)
              .attr('fill', (d, i) => {
                // if (this.#categories.length > 1) {
                //   return colourScale(d[this.#categoryKey])
                // }
                // else {
                //   return this.#colourSeries[rectCount++ % this.#colourSeries.length];
                // }
                return determineRectFill(d, i, d[this.#categoryKey])
              })
              .attr('class', d => {
                return categoryLookup[d[this.#categoryKey]]
              })
              .attr(y, d => {
                return nScale(lowestNValue);
              })
              .attr(x, (d, i) => {
                // return cSubScale(d.type) + cScale(d.cat)
                return cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d)
              })
              .attr(w, barWidth)
              .attr("opacity", 0)
              .transition()
              .duration(this.#transitionDuration)
              .attr("opacity", 1)
              .attr(h, d => {
                let height = Math.abs(nScale(d[this.#nKey]) - nScale(lowestNValue))
                return height == 0 || isNaN(height) ? 0.1 : height
              })
              .attr(y, d => {
                const input = isNaN(d[this.#nKey]) ? 0 : d[this.#nKey];
                return vertical ?
                  nScale(input) :
                  nScale(lowestNValue);
                // return nScale(input)
              })

            rect
              .on('mouseenter', tooltipEnter)
              .on('mouseleave', tooltipLeave)
              .on('mousemove', tooltipMove)

            // if (this.#interactive) {
            rect.attr('cursor', this.#interactive ? 'pointer' : 'auto')
            // }

            // creates bar labels
            if (barLabels) {
              let text = g
                .selectAll('text')
                .data(d => d[1])
                .join('text')

              text
                .attr('class', d => {
                  return `bar-label ${categoryLookup[d[this.#categoryKey]]}-label`
                })
                .attr('data-raw-value', d => {
                  let val = d[this.#nKey]
                  return val;
                })
                .attr('fill', darkFontColour)
                .attr("alignment-baseline", 'middle')
                .attr('dominant-baseline', 'middle')
                .attr('text-anchor', verticalTextAnchor)
                .attr('opacity', 0)
                .attr(x, (d, i) => {
                  // return cSubScale(d.type) + cScale(d.cat) + barWidth / 2
                  // return cSubScale(d.type) + this.#calcGroupedXPos(d) + barWidth / 2
                  return cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + barWidth / 2
                })
                .attr(y, d => {
                  // const input = (typeof d.val !== 'number') ? 0 : d.val;
                  // return nScale(lowestNValue) + (vertical ? -10 : 5);
                  // const input = isNaN(d[this.#nKey]) ? 0 : d[this.#nKey];
                  // const input = isNaN(d[this.#nKey]) ? 0 : (this.#displayUncertainties ? d[this.#upperUncertainty] : d[this.#nKey]);
                  const input = isNaN(d[this.#nKey]) ? 0 : (this.#displayUncertainties && d[this.#upperUncertainty] ? d[this.#upperUncertainty] : d[this.#nKey]);
                  // console.log(input)
                  return nScale(input) + (vertical ? -10 : 5)
                })
                .on('mouseenter', tooltipEnter)
                .on('mouseleave', tooltipLeave)
                .on('mousemove', tooltipMove)

              text
                .transition()
                .duration(this.#transitionDuration)
                .attr(y, d => {
                  // const input = isNaN(d[this.#nKey]) ? 0 : d[this.#nKey];
                  // const input = isNaN(d[this.#nKey]) ? 0 : (this.#displayUncertainties ? d[this.#upperUncertainty] : d[this.#nKey]);
                  const input = isNaN(d[this.#nKey]) ? 0 : (this.#displayUncertainties && d[this.#upperUncertainty] ? d[this.#upperUncertainty] : d[this.#nKey]);
                  return nScale(input) + (vertical ? -10 : 5)
                })
                .attr('opacity', function(d) {
                  let dimensions = that.#calculateTextDimensions(d.val, that.#getFullFont(this))
                  return that.#labelFitsGroupedBar(dimensions.width, dimensions.height, d) ? 1 : 0;
                })
                .tween("text", function(d) {
                  let selection = d3.select(this);
                  return that.#barLabelTweenGrouped(selection, d)
                })
                .on('end', function(d) {
                  let selection = d3.select(this);
                  selection.attr('display', function(d) {
                    let dimensions = that.#calculateTextDimensions(d.val, that.#getFullFont(this))
                    return that.#labelFitsGroupedBar(dimensions.width, dimensions.height, d) ? 'block' : 'none';
                  })
                })
            }

            //creates uncertainties
            if (this.#displayUncertainties) {
              g
                .selectAll('g.uncertainty')
                .data(d => d[1])
                .join(
                  enter => {


                    let g = enter.append('g')
                    g
                      .attr('class', 'uncertainty')
                      .attr('data-category', d => categoryLookup[d[this.#categoryKey]])

                    createUncertaintyLine(g, 'top', this.#upperUncertainty, false)
                    createUncertaintyLine(g, 'bottom', this.#lowerUncertainty, false)
                    createUncertaintyLine(g, 'connector')
                  }
                )
            }
          },
          update => {
            // console.log(update)
            let g = update
              .attr('class', 'bar-group')
              .attr('aria-label', d => {
                // console.log(d)
                return d[0] // key
              })

            this.#cSeries.map((c, i) => {
              if (i != 0) {
                g
                  .selectAll(`g[data-layer='${i}']`)
                  .data(d => {
                    return d[1]
                  })
                  // .join('g')
                  .join(
                    enter => {
                      g = enter.append('g')
                        .attr('class', 'bar-group')
                        .attr('aria-label', d => {
                          // console.log(d)
                          return d[0] // key
                        })
                        .attr('data-layer', i)
                        .attr('opacity', 1)
                    },
                    update => {
                      let newg = update
                        .attr('class', 'bar-group')
                        .attr('aria-label', d => {
                          // console.log(d)
                          return d[0] // key
                        })
                        .attr('data-layer', i)
                        .transition().duration(this.#transitionDuration)
                        .attr('opacity', 1)
                      g = g.merge(newg)
                    },
                    exit => {
                      //remove rectangles in removed groups to be removed
                      exit.selectAll('rect').transition().duration(this.#transitionDuration)
                        // .attr('opacity', 0)
                        .attr(h, 0)
                        .attr(y, nScale(lowestNValue))
                        .remove()

                      exit.selectAll('text').transition().duration(this.#transitionDuration)
                        .attr(y, nScale(lowestNValue))
                        .remove()

                      //remove groups
                      exit
                        .attr('opacity', 1)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)
                        .remove();
                    }
                  )

                // g
                //   .attr('class', 'bar-group')
                //   .attr('aria-label', d => {
                //     // console.log(d)
                //     return d[0] // key
                //   })
                //   .attr('data-layer', i)
              }
            })

            let updateRect = selection => {
              selection
                .attr('aria-label', d => {
                  if (this.#categoryKey) {
                    return `${d[this.#categoryKey]}: ${d[this.#nKey]}`
                  }
                  else {
                    return `${this.#getLabel(d[this.#nKey], proportional)}`
                  }
                })
                .attr(w, function(d) {
                  let value = d3.select(this).attr(w)
                  if (value === null)
                    return barWidth;
                  else
                    return value;
                })
                .attr(x, function(d, i) {
                  let value = d3.select(this).attr(x)
                  if (value === null)
                    // return cSubScale(d.type) + cScale(d.cat);
                    return cSubScale(d[that.#categoryKey]) + that.#calcGroupedXPos(d)
                  else
                    return value;
                })
                .attr(y, function(d) {
                  let value = d3.select(this).attr(y)
                  if (value === null)
                    return nScale(lowestNValue);
                  else
                    return value;
                })
                .on('mouseenter', tooltipEnter)
                .on('mouseleave', tooltipLeave)
                .on('mousemove', tooltipMove)
                .transition()
                .duration(this.#transitionDuration)
                .attr('opacity', 1)
                .attr('fill', (d, i) => {
                  // if (this.#categories.length > 1) {
                  //   return colourScale(d[this.#categoryKey])
                  // }
                  // else {
                  //   return this.#colourSeries[rectCount++ % this.#colourSeries.length];
                  // }
                  return determineRectFill(d, i, d[this.#categoryKey])
                })
                .attr('class', d => categoryLookup[d[this.#categoryKey]])
                .attr(x, (d, i) => {
                  // return cSubScale(d.type) + cScale(d.cat)
                  // return cSubScale(d.type) + this.#calcGroupedXPos(d)
                  // console.log(x, cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d))
                  return cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d)
                })
                .attr(w, barWidth)
                .attr(h, d => {
                  // let height = Math.abs(nScale(d.val) - nScale(lowestNValue))
                  // return height == 0 ? 0.1 : height
                  let height = Math.abs(nScale(d[this.#nKey]) - nScale(lowestNValue))
                  return height == 0 || isNaN(height) ? 0.1 : height
                })
                .attr(y, d => {
                  const input = isNaN(d[this.#nKey]) ? 0 : d[this.#nKey];
                  return vertical ?
                    nScale(input) :
                    nScale(lowestNValue);
                })

              // if (this.#interactive) {
              selection.attr('cursor', this.#interactive ? 'pointer' : 'auto')
              // }
            }

            let rect = g
              .selectAll('rect')
              .data(d => d[1])
              .join(
                enter => {
                  updateRect(enter.append('rect'))
                },
                update => {
                  // console.log('updateRect', update)
                  updateRect(update)
                },
                exit => {
                  exit.transition().duration(this.#transitionDuration)
                    .attr('opacity', 0)
                    .attr(h, 0)
                    .attr(y, nScale(lowestNValue))
                    .remove()
                }
              )

            //update bar Labels
            if (barLabels) {
              let updateText = selection => {
                selection
                  .attr('class', d => {
                    return `bar-label ${categoryLookup[d[this.#categoryKey]]}-label`
                  })
                  .attr("alignment-baseline", 'middle')
                  .attr('dominant-baseline', 'middle')
                  .attr('text-anchor', verticalTextAnchor)
                  .attr(x, function(d, i) {
                    let value = d3.select(this).attr(x)
                    if (value === null)
                      return cSubScale(d[that.#categoryKey]) + that.#calcGroupedXPos(d) + barWidth / 2;
                    else
                      return value;
                  })
                  .attr(y, function(d) {
                    let value = d3.select(this).attr(y)
                    if (value === null)
                      return nScale(lowestNValue);
                    else
                      return value;
                  })
                  .attr('display', 'block')
                  .on('mouseenter', tooltipEnter)
                  .on('mouseleave', tooltipLeave)
                  .on('mousemove', tooltipMove)
                // .text(d => (typeof d.val !== 'number') ? 'NA' : d.val);

                selection
                  .transition()
                  .duration(this.#transitionDuration)
                  .attr(y, d => {
                    // const input = (typeof d.val !== 'number') ? 0 : d[this.#nKey];
                    // return nScale(input) + (vertical ? -10 : 5);
                    // const input = isNaN(d[this.#nKey]) ? 0 : d[this.#nKey];
                    // const input = isNaN(d[this.#nKey]) ? 0 : (this.#displayUncertainties ? d[this.#upperUncertainty] : d[this.#nKey]);
                    const input = isNaN(d[this.#nKey]) ? 0 : (this.#displayUncertainties && d[this.#upperUncertainty] ? d[this.#upperUncertainty] : d[this.#nKey]);
                    // console.log('updateY', input)
                    return nScale(input) + (vertical ? -10 : 5)
                  })
                  .attr(x, (d, i) => {
                    // return cSubScale(d.type) + cScale(d.cat) + barWidth / 2;
                    return cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + barWidth / 2
                  })
                  .attr('fill', darkFontColour)
                  .attr('opacity', function(d) {
                    let dimensions = that.#calculateTextDimensions(d.val, that.#getFullFont(this))
                    return that.#labelFitsGroupedBar(dimensions.width, dimensions.height, d) ? 1 : 0;
                  })
                  .tween("text", function(d) {
                    let selection = d3.select(this);
                    return that.#barLabelTweenGrouped(selection, d)
                  })
                  .attr('data-raw-value', function(d) {
                    let selection = d3.select(this);
                    let val = d[that.#nKey];
                    if (!isNaN(val) && isNaN(selection.attr('data-raw-value'))) {
                      selection.attr('data-raw-value', 0);
                    }
                    return val;
                  })
                  .on('end', function(d) {
                    let selection = d3.select(this);
                    selection.attr('display', function(d) {
                      let dimensions = that.#calculateTextDimensions(d.val, that.#getFullFont(this));
                      return that.#labelFitsGroupedBar(dimensions.width, dimensions.height, d) ? 'block' : 'none';
                    })
                  })
              }

              let text = g
                .selectAll('text')
                .data(d => d[1])
                .join(
                  enter => {
                    updateText(enter.append('text'))
                  },
                  update => {
                    updateText(update)
                  },
                  exit => {
                    exit
                      .transition()
                      .duration(this.#transitionDuration)
                      .attr('opacity', 0)
                      .attr(y, nScale(lowestNValue))
                      .remove()
                  }
                )
            }

            //update uncertainties
            if (this.#displayUncertainties) {
              g
                .selectAll('g.uncertainty')
                .data(d => d[1])
                .join(
                  enter => {
                    let g = enter.append('g')
                    g
                      .attr('class', 'uncertainty')

                    createUncertaintyLine(g, 'top', this.#upperUncertainty, false)
                    createUncertaintyLine(g, 'bottom', this.#lowerUncertainty, false)
                    createUncertaintyLine(g, 'connector')
                  },
                  update => {
                    // console.log('uncertaintyUpdate', update, g)
                    update.transition().duration(this.#transitionDuration)
                      .attr('opacity', 1)
                    this.#updateUncertaintyLine(update.select(`line[data-uncertainty='top']`), this.#upperUncertainty, false)
                    this.#updateUncertaintyLine(update.select(`line[data-uncertainty='bottom']`), this.#lowerUncertainty, false)
                    this.#updateUncertaintyLine(update.select(`line[data-uncertainty='connector']`))
                  },
                  exit => {
                    exit
                      .transition()
                      .duration(this.#transitionDuration)
                      .attr('opacity', 0)
                      .attr(y, nScale(lowestNValue))
                      .remove()
                  }
                )
            }
          },
          exit => {
            // console.log(exit.selectAll('*'))
            // exit.selectAll('*')
            //   .transition()
            //   .duration(this.#transitionDuration)
            //   .attr('opacity', 0)
            //   .attr(h, 0)
            //   .attr(y, nScale(lowestNValue))
            //   .on('end', () => {
            //     console.log('end remove everything')
            //     exit.remove()
            //   })
            exit.selectAll('*')
              .transition()
              .duration(this.#transitionDuration)
              .attr('opacity', 0)
              .attr(h, 0)
              .attr(y, nScale(lowestNValue))
              .remove()
            // exit.selectAll('rect')
            //   .transition()
            //   .duration(this.#transitionDuration)
            //   .attr('opacity', 0)
            //   .attr(h, 0)
            //   .attr(y, nScale(lowestNValue))
            //   .on('end', () => {
            //     console.log('end remove everything')
            //     exit
            //       .remove()
            //   })

            // if (barLabels) {
            //   exit.selectAll('text')
            //     .transition()
            //     .duration(this.#transitionDuration)
            //     .attr('opacity', 0)
            //     .attr(y, nScale(lowestNValue))
            // }

            // if (this.#displayUncertainties) {
            //   exit.selectAll('g.uncertainty')
            //     .transition()
            //     .duration(this.#transitionDuration)
            //     .attr(y, nScale(lowestNValue))
            //     .attr('opacity', 0)
            // }


          }
        )
    }
  }
  #renderAverageLines() {
    if (!this.#averageGroup)
      this.#averageGroup = this.#container.append('g').attr('class', 'averageLines')

    this.#averageGroup.selectAll("line")
      .data(this.#averageLines)
      .join(
        enter => {
          let line = enter.append('line')
          // .attr("transform", d => `translate(${this.#cScale(d[this.#cKey])}, ${this.#nScale(d[this.#nKey])})`)
          let x1 = this.#vertical ? 'x1' : 'y1'
          let x2 = this.#vertical ? 'x2' : 'y2'
          let y1 = this.#vertical ? 'y1' : 'x1'
          let y2 = this.#vertical ? 'y2' : 'x2'

          let x1Value = this.#vertical ?
            this.#margins.l :
            this.#margins.t;
          let x2Value = this.#vertical ?
            this.#width - this.#margins.r :
            this.#height - this.#margins.b;

          line
            .attr(y1, d => this.#nScale(d))
            .attr(y2, d => this.#nScale(d))
            .attr(x1, x1Value)
            .attr(x2, x2Value)
            .attr("stroke", (d, i) => this.#averageLinesColours[i])
            .attr("stroke-width", 2)
            .style("stroke-dasharray", (d, i) => {
              // console.log(d)
              if (!this.#averageLinesType) {
                return 0
              }
              if (this.#averageLinesType[i] == "dashed") {
                return 10
              }
              else if (this.#averageLinesType[i] == "dotted") {
                return 4
              }
              else if (this.#averageLinesType[i] == "solid") {
                return 0
              }
            })
        }
      )
  }
  #renderAverageLinesLegend() {
    this.#legendGroup
      .selectAll('g.average-group')
      .data(this.#averageLines)
      .join(
        enter => {
          let lineLength = 30;
          let textOffset = this.#legendTextOffset
          const r = this.#legendRadius;
          const circleSpacing = this.#legendCircleSpacing;
          const secondaryCircleSpacing = this.#legendSecondaryCircleSpacing;
          const spaceFromGraph = this.#legendSpacingFromGraph;
          const heightFromTop = this.#margins.t
          const legendPosition = this.#legendPosition ?? [this.#width - this.#margins.l - this.#margins.r + spaceFromGraph, heightFromTop]

          let g = enter.append('g');
          g
            .attr('class', d => 'average-group')
            // .attr('data-category', (d, i) => this.#categoryLookup[d])
            // .attr('transform', (d, i) => `translate(${this.#legendOrientation == "h" ? legendIntervalSpacing * i : 0}, ${this.#legendOrientation == "v" ? legendIntervalSpacing * i : 0})`)
            .attr('transform', (d, i) => `translate(${legendPosition[0] - lineLength + (this.#legendOrientation == 'v' ? 0 : circleSpacing * i)}, ${legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0) + 30})`)
            .attr('opacity', 0)
            .transition()
            .duration(this.#transitionDuration)
            .attr('opacity', 1)

          g.append('line')
            .attr("stroke", (d, i) => this.#averageLinesColours[i])
            .attr("stroke-width", 2)
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", lineLength)
            .attr("y2", 0)
            .style("stroke-dasharray", (d, i) => {
              // console.log(d)
              if (!this.#averageLinesType) {
                return 0
              }
              if (this.#averageLinesType[i] == "dashed") {
                return 10
              }
              else if (this.#averageLinesType[i] == "dotted") {
                return 4
              }
              else if (this.#averageLinesType[i] == "solid") {
                return 0
              }
            })
            .attr("opacity", 1)

          let text = g.append('text')
            .attr('x', lineLength + textOffset)
            .attr('y', 0)
            .attr('dy', 0)
            .attr('alignment-baseline', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('opacity', 1)
            .text((d, i) => {
              if (this.#averageLinesLegendText && this.#averageLinesLegendText[i]) {
                return this.#averageLinesLegendText[i]
              }
              return d
            })
        }
      )
  }
  //nested cAxis stuff
  #renderFancyAxes(axesGroup, orientation) {
    let that = this;
    const height = this.#vertical ?
      this.#height - this.#margins.b :
      0;

    let axisInitialHeight = this.#cAxisInitialHeight;
    let axisDrop = this.#cAxisDrop;
    let hAxis;

    function addAxis(selection, axisGen, i, yPos, xPos, series = null, displayPath = true) {
      if (series == null) {
        // console.log("nullPosition", xPos, height)
        hAxis = selection
          .append('g')
          .attr('class', orientation + i)
          .attr('transform', `translate(${xPos}, ${height})`)
          // .attr('transform', `translate(${height}, ${0})`)
          .call(axisGen)
      }
      else {
        // console.log(selection)
        let trans = -that.#cScales[i - 1].bandwidth() / 2
        let transX = that.#vertical ? trans : 0;
        let transY = that.#vertical ? 0 : trans;
        hAxis = selection.selectAll('g')
          .data(series)
          .append('g')
          .attr('transform', `translate(${transX}, ${transY})`)
          .attr('class', orientation + i)
          .call(axisGen)
        // console.log(hAxis)
      }
      let cAxisTitleExists = that.#cAxisTitle && that.#cAxisTitle.trim() != "";
      let wrapWidth = that.#vertical ?
        // that.#cScales[i].bandwidth() + that.#cScales[i].padding()
        that.#cScales[i].step() :
        (cAxisTitleExists ? that.#cAxisTitleSpacing : that.#margins.l); //that.#cAxisTitleSpacing
      let fitWidth = that.#vertical ? (cAxisTitleExists ? that.#cAxisTitleSpacing : that.#margins.b) : (cAxisTitleExists ? that.#cAxisTitleSpacing : that.#margins.l);

      let hAxisYPos = that.#vertical ? yPos : 0;
      let hAxisXPos = that.#vertical ? 0 : yPos;


      if (that.#fitTickText) {
        // console.log("wrapWidth", wrapWidth)
        hAxis
          .selectAll('.tick text')
          .attr('transform', `translate(${hAxisXPos}, ${hAxisYPos})`)
          .call(that.#wrap, wrapWidth)
          .call(that.#fitToConstraints, that.#vertical ? that.#cAxisTitleSpacing : that.#cScales[i].bandwidth() + that.#cScales[i].padding(), that) //that.#cAxisTitleSpacing
        // .call(that.#fitToConstraints, that.#cAxisTitleSpacing, that) //that.#cAxisTitleSpacing
      }
      else {
        hAxis
          .selectAll('.tick text')
          .attr('transform', `translate(${hAxisXPos}, ${hAxisYPos})`)
        // .call(that.#wrap, wrapWidth)
      }




      hAxis
        .selectAll('.tick line')
        .attr('y1', 0)
        .attr('y2', 0)
        .attr('x1', 0)
        .attr('x2', 0)

      if (!displayPath) {
        hAxis.select("path").remove()
      }
    }
    // console.log(this.#axisGens);
    this.#axisGens[orientation].map((cAxisGen, i) => {
      let yPos = that.#vertical ? axisInitialHeight - axisDrop * i : -axisInitialHeight + axisDrop * i;
      let xPos = that.#vertical ? 0 : that.#margins.l;
      if (i == 0) {
        addAxis(axesGroup, cAxisGen, i, yPos, xPos)
      }
      else {
        // console.log(this.#surKeys[i-1])
        addAxis(hAxis, cAxisGen, i, yPos, xPos, this.#surKeys[i - 1], false)
      }
    })
  }
  #renderAxes() {
    const that = this;
    // console.log("axisGens", this.#axisGens)
    // Create subgroup

    if (!this.#axesGroup)
      this.#axesGroup = this.#container.append('g').attr('class', 'axes');
    const axes = this.#axesGroup

    // Render vertical axis
    const v = this.#vertical ? 'n' : 'c';
    if (v != 'c') {
      let vAxis = axes
        .append('g')
        .attr('class', v)
        .attr('transform', `translate(${this.#margins.l},0)`)
        .call(this.#axisGens[v]);
    }
    else {
      this.#renderFancyAxes(axes, v)
      // vAxis
      //   .selectAll('.tick text')
      // .call(this.#wrap, this.#cAxisTitleSpacing - 10) //replace 10 with fontsize of axis title/2, but would need to have the fontsize as a class attribute instead of css (or change load order of render title and renderAxes, then read the fontSize with getCssProperty)
      // .call(this.#fitToConstraints, this.#cScale.bandwidth() + this.#cScale.padding(), this)
    }

    // Render horizontal axis
    const h = this.#vertical ? 'c' : 'n';
    const height = this.#vertical ?
      this.#height - this.#margins.b :
      this.#height - this.#margins.b;
    if (h != 'c') {
      let hAxis = axes
        .append('g')
        .attr('class', h)
        .attr('transform', `translate(0, ${height})`)
        .call(this.#axisGens[h])
    }
    else {
      this.#renderFancyAxes(axes, h)
    }
  }
  #updateAxes() {
    const that = this;
    const axes = this.#axesGroup

    // update vertical axis
    const v = this.#vertical ? 'n' : 'c';

    let vText = []
    axes
      .select(`.${v}`)
      .selectAll('.tick text')
      .each(el => vText.push(el))

    // console.log(hText, this.#cScale.domain())
    if (v == 'n') {
      axes
        .select(`.${v}`)
        .transition().duration(this.#transitionDuration)
        .call(this.#axisGens[v]);
    }
    else {
      let joinAxisText = () => {
        let arrayOfJoins = [];
        this.#cSeries.map((c, i) => {
          //get text for each cSeries row before being replaced to use for transition comparing down the line
          let cText = []
          axes
            .selectAll(`.${v + i} > .tick > text`)
            .each(el => cText.push(el))
          //ensure the text array is unique to match the domain format
          // myArray.push([... new Set(cText)].join(""))
          arrayOfJoins.push(cText.join(""))
        })
        return arrayOfJoins;
      }
      //get hAxis text
      let vText = joinAxisText();

      //remove axes
      axes.select(`.${v}0`).remove();
      //render axes again
      this.#renderFancyAxes(axes, v)
      //get newly rendered hAxis text
      let newVText = joinAxisText();
      //find which need to be transitioned in by comparing past axis text to new axis text
      this.#cSeries.map((c, i) => {
        if (newVText[i] != vText[i])
          axes.selectAll(`.${v + i} > .tick > text`)
          .attr('opacity', 0)
          .transition().duration(this.#transitionDuration)
          .attr("opacity", 1)
      })
    }

    // update horizontal axis
    const h = this.#vertical ? 'c' : 'n';

    const height = this.#vertical ?
      this.#height - this.#margins.b :
      this.#height - this.#margins.b;

    if (h == 'n') {
      axes
        .select(`.${h}`)
        .transition().duration(this.#transitionDuration)
        .call(this.#axisGens[h]);
    }
    else {
      let joinAxisText = () => {
        let arrayOfJoins = [];
        this.#cSeries.map((c, i) => {
          //get text for each cSeries row before being replaced to use for transition comparing down the line
          let cText = []
          axes
            .selectAll(`.${h + i} > .tick > text`)
            .each(el => cText.push(el))
          //ensure the text array is unique to match the domain format
          // myArray.push([... new Set(cText)].join(""))
          arrayOfJoins.push(cText.join(""))
        })
        return arrayOfJoins;
      }
      //get hAxis text
      let hText = joinAxisText();

      //remove axes
      axes.select(`.${h}0`).remove();
      //render axes again
      this.#renderFancyAxes(axes, h)
      //get newly rendered hAxis text
      let newHText = joinAxisText();
      //find which need to be transitioned in by comparing past axis text to new axis text
      this.#cSeries.map((c, i) => {
        if (newHText[i] != hText[i])
          axes.selectAll(`.${h + i} > .tick > text`)
          .attr('opacity', 0)
          .transition().duration(this.#transitionDuration)
          .attr("opacity", 1)
      })
    }
  }
  #renderTitles() {
    // Create subgroup 
    if (!this.#titleGroup)
      this.#titleGroup = this.#container.append('g').attr('class', 'titles')

    const titles = this.#titleGroup

    const graphTitle = titles.select('.graph-title')

    // Render chart title
    if (graphTitle.empty() && this.#graphTitle) {
      //add title
      titles
        .append('text')
        .attr('class', 'graph-title')
        .attr('x', (this.#width - this.#margins.r) / 2)
        .attr('y', this.#margins.t / 2)
        .attr('dy', 0)
        .attr('opacity', 1)
        .attr('text-anchor', 'middle')
        .text(this.#graphTitle)
        .call(this.#wrap, this.#width - this.#width * 0.1)
    }
    else if (!graphTitle.empty() && graphTitle.text() !== this.#graphTitle) {
      //transition existing title to new title
      graphTitle
        .attr('opacity', 0)
        .text(this.#graphTitle)
        .call(this.#wrap, this.#width - this.#width * 0.1)
      graphTitle
        .transition()
        .duration(this.#transitionDuration)
        .attr('opacity', 1)
      // .transition()
      // .duration(this.#transitionDuration / 2)
      // .attr('opacity', 0)
      // .on('end', () => {
      //   graphTitle.text(this.#graphTitle)

      //   graphTitle
      //     .transition()
      //     .duration(this.#transitionDuration / 2)
      //     .attr('opacity', 1)
      // })
    }


    const height = this.#height;
    const v = this.#vertical ? 'n' : 'c';
    const vTitle = this.#vertical ? this.#nAxisTitle : this.#cAxisTitle;
    const vSpacing = this.#vertical ? this.#nAxisTitleSpacing : this.#cAxisTitleSpacing;
    const vAxis = titles.select(`.${v}-axis-title`)
    let vAxisText;
    if (!vAxis.empty()) {
      vAxisText = Array.from(vAxis.selectAll("tspan")._groups[0])
        .map(tspan => d3.select(tspan).text()).join(" ")
    }

    const vtAxisLength = height + this.#margins.t - this.#margins.b

    // Render axis titles
    if (vAxis.empty()) {
      let vt = titles
        .append('text')
        .attr('class', v + '-axis-title')
        .attr('opacity', 1)
        .attr('x', (-height - this.#margins.t + this.#margins.b) / 2)
        .attr('y', () => {
          return this.#margins.l - vSpacing;
        })
        .attr('dy', 0)
        .attr('transform', `rotate(-90)`)
        .attr('text-anchor', 'middle')
        .attr('alignment-baseline', v == 'c' ? "after-edge" : null)
        .attr('dominant-baseline', v == 'c' ? "hanging" : null)
        .html(vTitle);

      vt.call(this.#wrap, vtAxisLength - vtAxisLength * 0.2)
    }
    else if (vAxisText !== vTitle) {
      // console.log(vAxis.join(" "))

      vAxis
        .attr('opacity', 0)
        .text(vTitle)
        .call(this.#wrap, vtAxisLength - vtAxisLength * 0.2)

      vAxis
        .transition()
        .duration(this.#transitionDuration)
        .attr('opacity', 1)
      // .transition()
      // .duration(this.#transitionDuration / 2)
      // .attr('opacity', 0)
      // .on('end', () => {
      //   vAxis.text(vTitle)
      //   vAxis
      //     .transition()
      //     .duration(this.#transitionDuration / 2)
      //     .attr('opacity', 1)
      // })
    }

    const h = this.#vertical ? 'c' : 'n';
    const hTitle = this.#vertical ? this.#cAxisTitle : this.#nAxisTitle;
    const hSpacing = this.#vertical ? this.#cAxisTitleSpacing : this.#nAxisTitleSpacing;
    const hAxis = titles.select(`.${h}-axis-title`)

    if (hAxis.empty()) {
      titles
        .append('text')
        .attr('class', h + '-axis-title')
        .attr('opacity', 1)
        .attr('x', (this.#width + this.#margins.l - this.#margins.r) / 2)
        .attr('y', height - this.#margins.b + hSpacing)
        .attr('text-anchor', 'middle')
        .attr('alignment-baseline', h == 'c' ? "before-edge" : null)
        .attr('dominant-baseline', h == 'c' ? "hanging" : null)
        .html(hTitle);
    }
    else if (hAxis.text() !== hTitle) {
      hAxis
        .attr('opacity', 0)
        .html(hTitle)
      hAxis
        .transition()
        .duration(this.#transitionDuration)
        .attr('opacity', 1)
      // hAxis
      //   .transition()
      //   .duration(this.#transitionDuration / 2)
      //   .attr('opacity', 0)
      //   .on('end', () => {
      //     hAxis.text(hTitle)
      //     hAxis
      //       .transition()
      //       .duration(this.#transitionDuration / 2)
      //       .attr('opacity', 1)
      //   })
    }
  }
  #addBarHoverFade() {
    let that = this;
    this.#barGroup
      .on('mouseover.fade', function(e, d) {

        let current = d3.select(e.target)
        let targetClass = current.attr('class')

        that.#barGroup.selectAll(`rect:not(.${targetClass})`)
          .attr('opacity', 0.3)

        that.#barGroup.selectAll(`rect.${targetClass}`)
          .attr('stroke', 'black')
      })
      .on('mouseout.fade', function(e, d) {
        let current = d3.select(e.target)
        let targetClass = current.attr('class')

        d3.selectAll(`rect:not(.${targetClass})`)
          .attr('opacity', 1)

        that.#barGroup.selectAll(`rect.${targetClass}`)
          .attr('stroke', null)
      })

    // console.log(this.#barGroup.selectAll('rect'))
  }
  #addLegendHoverFade() {
    if (!this.#selectedCategories) {
      this.#selectedCategories = this.#findSelectedValues();
    }
    // let that = this;

    //mouseover
    let fadeOut = (selection) => {
      this.#selectedCategories = this.#findSelectedValues();

      let targetClass = selection.attr('class').split(" ")[0]

      this.#selectedCategories = this.#findSelectedValues();
      let rectSelectorArray = [];
      let legendSelectorArray = [];
      this.#selectedCategories.map(el => {
        if (el != targetClass) {
          rectSelectorArray.push(`rect.${el}`);
          legendSelectorArray.push(`circle.${el},text.${el}`)
        }
      })

      if (rectSelectorArray.length != 0) {
        let rectSelector = rectSelectorArray.join(",");
        let legendSelector = legendSelectorArray.join(",");

        let rectGroups = this.#barGroup.selectAll(rectSelector)
        let legendGroups = this.#legendGroup.selectAll(legendSelector);

        rectGroups
          .attr('opacity', 0.3)

        legendGroups
          .attr('opacity', 0.3)
      }

      this.#barGroup.selectAll(`rect.${targetClass}`)
        .attr('stroke', 'black')

      this.#legendGroup.selectAll(`circle.${targetClass}`)
        .attr('stroke', 'black')
    }

    //mouseout
    let fadeIn = (selection) => {

      let targetClass = selection.attr('class').split(" ")[0];

      this.#selectedCategories = this.#findSelectedValues();

      let rectSelector = this.#selectedCategories.map(el => `rect.${el}`).join(",");
      let legendSelector = this.#selectedCategories.map(el => `circle.${el},text.${el}`).join(",");

      let rectGroups = this.#barGroup.selectAll(rectSelector);
      let legendGroups = this.#legendGroup.selectAll(legendSelector);

      // console.log(selector)

      rectGroups //:not(.${targetClass})
        .attr('opacity', 1)
      legendGroups
        .attr('opacity', 1)

      this.#barGroup.selectAll(`rect.${targetClass}`)
        .attr('stroke', null)

      this.#legendGroup.selectAll(`circle.${targetClass}`)
        .attr('stroke', null)
    }

    this.#legendGroup.selectAll('.legend-group')
      .on('mouseover.fade', function(e, d) {
        fadeOut(d3.select(e.target))
      })
      .on('mouseout.fade', function(e, d) {
        fadeIn(d3.select(e.target))
      })
      .on('focus.fade', function(e, d) {
        fadeOut(d3.select(e.target).select('circle'))
      })
      .on('focusout.fade', function(e, d) {
        fadeIn(d3.select(e.target).select('circle'))
      })
  }
  #addInteraction() {
    const bars = this.#container
    // .select('.bars');

    // const legend = this.#container
    //   .select('.legend');

    const legend = this.#legendGroup;

    // Save private fields (can't access 'this' when rendering bars)
    const that = this;
    const cSeries = this.#cSeries;
    const categories = this.#categories;
    let nScale = this.#nScale;
    const cScale = this.#cScales[this.#cScales.length - 1];
    const cSubScale = this.#cSubScale;
    const barWidth = this.#barWidth;
    const graphWidth = this.#width;
    const barLabels = this.#barLabels;
    const proportional = this.#proportional;
    const height = this.#vertical ?
      this.#height - this.#margins.b :
      this.#height - this.#margins.b;

    let cKeys = this.#cKeys;

    const transitionDuration = this.#transitionDuration;

    const bottomAxisPosition = this.#height - this.#margins.b;
    const leftAxisPosition = 0 + this.#margins.l;

    // Vertical / horizontal adjustment
    const vertical = this.#vertical;
    const x = vertical ? 'x' : 'y';
    const y = vertical ? 'y' : 'x';
    const h = vertical ? 'height' : 'width';
    const w = vertical ? 'width' : 'height';

    // Create subgroups for each bar series
    const first = this.#vertical ? 0 : 1;
    const last = this.#vertical ? 1 : 0;


    const categoryLookup = this.#categoryLookup;
    const categoryReverseLookup = this.#categoryReverseLookup;

    let collapsed = false;
    let categoriesBeforeCollapse = []

    let selectedValues = [];

    function fadeLegendCenter(classVal) {
      legend.selectAll(`circle.${classVal}`)
        .attr("fill-opacity", 1)
        .transition()
        .duration(transitionDuration)
        .attr("fill-opacity", 0.5);

      legend.selectAll(`text.${classVal}`)
        .attr("opacity", 1)
        .transition()
        .duration(transitionDuration)
        .attr("opacity", 0.5);

      legend.selectAll(`circle.${classVal}`)
        .classed('selected', false);

      if (that.#htmlLegend) {
        that.#htmlLegend.selectAll(`li.${classVal}`)
          .classed('selected', false)
          .transition()
          .duration(transitionDuration)
          .style("opacity", 0.5);
      }
    }

    function reverseFadeCenter(classVal) {
      legend.selectAll(`circle.${classVal}`)
        .transition()
        .duration(transitionDuration)
        .attr("fill-opacity", 1);

      legend.selectAll(`text.${classVal}`)
        .transition()
        .duration(transitionDuration)
        .attr("opacity", 1);

      legend.selectAll(`circle.${classVal}`)
        .classed('selected', true);

      if (that.#htmlLegend) {
        that.#htmlLegend.selectAll(`li.${classVal}`)
          .classed('selected', true)
          .transition()
          .duration(transitionDuration)
          .style("opacity", 1);
      }
    }

    let shiftSelectedGroupRect = (barGroups) => {
      let lowestNValue = this.#grouped && this.#log ? this.#min : 0;
      //expand the rest of the selected bars
      let selector = this.#selectedCategories.map(el => `rect.${el}`).join(",");
      // console.log(selector)
      if (selector.length !== 0) {
        barGroups.selectAll(selector)
          .transition()
          .duration(this.#transitionDuration)
          .attr(w, cSubScale.bandwidth())
          .attr(x, (d, i) => {
            return cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d)
          })
          .attr(h, d => {
            let height = Math.abs(nScale(d[this.#nKey]) - nScale(lowestNValue))
            return height == 0 || isNaN(height) ? 0.1 : height
          })
          .attr(y, d => {
            const input = isNaN(d[this.#nKey]) ? 0 : d[this.#nKey];
            return vertical ?
              nScale(input) :
              nScale(lowestNValue);
          })
          .attr('opacity', 1)
      }
    }

    let shiftSelectedGroupUncertainties = () => {
      let uncertaintySelector = this.#selectedCategories.map(el => `g.uncertainty[data-category='${el}']`);
      // console.log("uncertaintySelector", uncertaintySelector)
      if (uncertaintySelector.length !== 0) {
        //grab those and move them to their new home :D. Before calling the method, hide the ones that don't fit
        bars.selectAll(uncertaintySelector).each(function(d) {
          // console.log(d, this)
          let uncertaintyGroup = d3.select(this)

          that.#updateUncertaintyLine(uncertaintyGroup.select(`line[data-uncertainty='top']`), that.#upperUncertainty, false)
          that.#updateUncertaintyLine(uncertaintyGroup.select(`line[data-uncertainty='bottom']`), that.#lowerUncertainty, false)
          that.#updateUncertaintyLine(uncertaintyGroup.select(`line[data-uncertainty='connector']`))
        })

      }
    }

    let shiftSelectedGroupLabels = () => {
      //for labels that stay
      let textSelector = this.#selectedCategories.map(el => `text.${el}-label`).join(",");
      if (textSelector.length !== 0) {
        let text_labels_stay = bars.selectAll(textSelector)
        text_labels_stay
          .transition()
          .duration(this.#transitionDuration)
          .attr(x, (d, i) => {
            return cSubScale(d[this.#categoryKey]) + this.#calcGroupedXPos(d) + cSubScale.bandwidth() / 2
          })
          .attr(y, d => {
            // const input = isNaN(d[this.#nKey]) ? 0 : d[this.#nKey];
            const input = isNaN(d[this.#nKey]) ? 0 : (this.#displayUncertainties && d[this.#upperUncertainty] ? d[this.#upperUncertainty] : d[this.#nKey]);
            return nScale(input) + (vertical ? -10 : 5)
          })
          .attr('opacity', function(d) {
            let dimensions = that.#calculateTextDimensions(d.val, that.#getFullFont(this))
            return that.#labelFitsGroupedBar(dimensions.width, dimensions.height, d) ? 1 : 0;
          })
      }
    }

    function calculateSubtractionValue(currIndex, removed, d) {
      // if (!proportional) {
      //non-proportional: sum the values of the removed items below the current index
      let subValue = 0

      removed.map(el => {
        let matchedGroup = true;
        cSeries.map(c => {
          if (el.data[c] != d[0].data[c]) {
            matchedGroup = false;
          }
        })
        if (categories.indexOf(el.key) < currIndex &&
          matchedGroup
        ) {
          subValue += el.value;
        }
      })
      return subValue;
      // }
      // else {
      //   //proportional: sum all the removed values in a group. NOT UPDATED
      //   let subValue = 0
      //   removed.map(el => {
      //     if (el.group == d.data[cSeries]) {
      //       subValue += el.value;
      //     }
      //   })
      //   return subValue;
      // }

    }

    let createNewProportionalData = (data, categories) => {

      cKeys = this.#createCKeys(data); // data

      // // Create stack first (data needed for yScale)
      // let stackGen = this.#createStackGen(categories); // categories

      // //if proportional, change the values as a percent value of the total
      // let stackData = this.#createProportionalStackData(data, categories, stackGen); // data, categories, stackGen

      // this.#proportionalStack = this.#rebaseStackData(stackData, cKeys)
      // //convert the stack such that it's rebased on the dependent variables instead of the independent

      this.initData(categories);

      return this.#proportionalStack; //stackData, cKeys
    }

    let getRowIdentifiers = (d) => {
      // console.log(d)
      let identifiers = [];

      this.#cSeries.map(c => {
        identifiers.push(d[0].data[c])
      })

      identifiers.push(d.key)

      return identifiers;
    }

    let getRowInData = (proportionalStack, identifiers, d) => {
      // console.log(subSeries, d)

      // let currentCValues = [];

      // this.#cSeries.map(c => {
      //   currentCValues.push(d[0].data[c])
      // })

      let layer = proportionalStack;

      identifiers.map((cVal, i) => {
        //if its a cSeries value
        if (i < this.#cSeries.length) {
          layer = layer.find(l => l[0] == cVal)[1]
        }
        //else its the category key value
        else {
          // console.log('isolate cat', layer)
          layer = layer.find(l => l.key == cVal)
        }
      })

      // console.log(layer)

      // let numSelected = subSeries.length;
      // let remainder = (i) % numSelected
      // let multiple = Math.floor((i) / numSelected)
      // console.log(proportionalStack, numSelected, i)

      // let row = proportionalStack[multiple][remainder]
      return layer;
    }

    let calculateProportionalYShift = (currIndex, subSeries, proportionalStack, i, notSelected, d) => {
      // for proportional, need to know what the value below it is, and shift to where it will go
      let shiftToY = 0;

      //a value of 0 would just need to return 0, hence the initial value
      if (currIndex > 0) {
        let breakLoop = false;
        //keep looking until either a value is found, or the index becomes negative
        for (let k = 1; currIndex - k > -1 && !breakLoop; k++) {
          let valBelow = categories[currIndex - k]
          let subIndexBelow = subSeries.indexOf(valBelow)
          //if index exists, then a value exists below it
          if (subIndexBelow > -1) {
            // let belowRow = getRowInData(proportionalStack, subSeries, Math.floor(i / notSelected.length) * (cKeys.length) + subIndexBelow, cKeys)
            // let belowRow = getRowInData(proportionalStack, subSeries, Math.floor(i / notSelected.length) * (cKeys.length) + subIndexBelow, cKeys)
            let identifiers = getRowIdentifiers(d);
            identifiers[identifiers.length - 1] = subSeries[subIndexBelow]
            let belowRow = getRowInData(proportionalStack, identifiers)[0];
            shiftToY = belowRow[1]
            breakLoop = true;
          }
        }
      }
      console.log()

      return shiftToY;
    }

    let removeBars = (classVal) => {
      //find selected categories
      this.#selectedCategories = this.#findSelectedValues()

      let subSeries = this.#selectedCategories.map(el => {
        return categoryReverseLookup[el]
      })

      this.#cSubScale = this.#cSubScale.domain(subSeries)

      //find categories that are not selected
      let notSelected = []
      this.#categories.map((el, i) => {
        let translatedEl = categoryLookup[el]
        if (!this.#selectedCategories.includes(translatedEl)) {
          notSelected.push(translatedEl)
        }
      })
      let notSelectorRect = notSelected.map(el => `rect.${el}`).join(",");
      let rectGroups = bars.selectAll(notSelectorRect)


      //is grouped
      if (this.#grouped) {
        let barGroups = bars.selectAll(".bar-group");
        //for selected legend class, remove those bars
        barGroups.selectAll(notSelectorRect)
          .transition()
          .duration(this.#transitionDuration)
          .attr('opacity', 0)
          .attr(y, function(d) {
            return vertical ? bottomAxisPosition : leftAxisPosition
          })
          .attr(h, 0.1)

        // shift bar labels
        if (barLabels) {
          let notSelectorText = notSelected.map(el => `text.${el}-label`).join(",");
          let textGroups = bars.selectAll(notSelectorText)

          //for labels that disappear
          textGroups
            .transition()
            .duration(this.#transitionDuration)
            .attr(y, d => {
              return vertical ? bottomAxisPosition : leftAxisPosition
            })
            .attr('opacity', 0)

          //for labels of still selected values
          shiftSelectedGroupLabels()
        }

        //shift uncertainties
        if (this.#displayUncertainties) {
          let notSelectorText = notSelected.map(el => `g.uncertainty[data-category='${el}']`).join(",");
          let uncertaintyGroups = bars.selectAll(notSelectorText)

          uncertaintyGroups.each(function(d) {
            // console.log(d, this)
            let uncertaintyGroup = d3.select(this)

            that.#updateUncertaintyLineRemove(uncertaintyGroup.select(`line[data-uncertainty='top']`), that.#upperUncertainty)
            that.#updateUncertaintyLineRemove(uncertaintyGroup.select(`line[data-uncertainty='bottom']`), that.#lowerUncertainty)
            that.#updateUncertaintyLineRemove(uncertaintyGroup.select(`line[data-uncertainty='connector']`))
          })

          shiftSelectedGroupUncertainties()
        }

        //move the rest of the selected bars to their respective locations 
        shiftSelectedGroupRect(barGroups)
      }
      //is stacked
      else {
        let proportionalStack = proportional ? createNewProportionalData(this.#data, subSeries) : null;

        let removed = []

        //for bars that need to be removed
        rectGroups
          .transition()
          .duration(this.#transitionDuration)
          .attr(h, 0.1)
          .attr('opacity', 0)
          .attr(y, function(d, i) {
            // let currentClass = d3.select(this).attr('class')
            // let currIndex = categories.indexOf(categoryReverseLookup[currentClass])
            let key = d.key;
            let currIndex = categories.indexOf(key);
            // console.log(d)

            //for each removed 
            removed.push({
              "key": key,
              "data": d[0].data, //group: d[cSeries]
              "value": Math.abs(d[0][last] - d[0][first])
            })

            let subValue = calculateSubtractionValue(currIndex, removed, d)
            // console.log(nScale(d[0][vertical ? first : last] - subValue))
            if (!proportional)
              return nScale(d[0][vertical ? first : last] - subValue);
            else {
              // return nScale((d[last] + d[first]) / 2)
              let shiftToY = calculateProportionalYShift(currIndex, subSeries, proportionalStack, i, notSelected, d)
              return nScale(shiftToY)
            }

          })
        if (barLabels) {
          let notSelectorText = notSelected.map(el => `text.${el}-label`).join(",");
          let textGroups = bars.selectAll(notSelectorText)

          //for text that needs to be removed
          textGroups
            .transition()
            .duration(this.#transitionDuration)
            .attr('opacity', 0)
            .attr(y, function(d, i) {
              let currentClass = d3.select(this).attr('class').split(" ")[1].replace("-label", "")
              let currIndex = categories.indexOf(categoryReverseLookup[currentClass])

              let subValue = calculateSubtractionValue(currIndex, removed, d)
              if (!proportional)
                return nScale(d[0][vertical ? first : last] - subValue);
              else {
                // return nScale((d[last] + d[first]) / 2)
                let shiftToY = calculateProportionalYShift(currIndex, subSeries, proportionalStack, i, notSelected, d)
                return nScale(shiftToY)
              }
            })
            .attr('display', 'none')
        }

        // console.log('removed', removed)

        //for bars not removed but that need to slide down
        let selectorRect = this.#selectedCategories.map(el => `rect.${el}`).join(",");

        if (selectorRect.length !== 0) {
          bars.selectAll(selectorRect)
            .transition()
            .duration(this.#transitionDuration)
            .attr(y, function(d, i) {
              // console.log(d)
              if (!proportional) {
                // const input = isNaN(d[this.#nKey]) ? 0 : d[this.#nKey];
                // return vertical ?
                //   nScale(input) :
                //   nScale(lowestNValue);
                // let currentClass = d3.select(this).attr('class')
                let currIndex = categories.indexOf(d.key)

                let subValue = calculateSubtractionValue(currIndex, removed, d)
                // console.log('subValueSlide', subValue, that.#stackData)
                return nScale(d[0][last] - subValue);
              }
              else {
                let identifiers = getRowIdentifiers(d);
                let row = getRowInData(proportionalStack, identifiers, d)[0]
                return nScale(row[last]);
              }

            })
            .attr('opacity', 1)
            .attr(h, (d, i) => {
              if (!proportional) {
                let height = nScale(d[0][first]) - nScale(d[0][last]);
                return height == 0 || isNaN(height) ? 0.1 : height
              }
              else {
                let identifiers = getRowIdentifiers(d);
                let row = getRowInData(proportionalStack, identifiers, d)[0]
                let height = nScale(row[first]) - nScale(row[last]);
                return height == 0 || isNaN(height) ? 0.1 : height;
              }
            })


          if (barLabels) {
            let selectorText = this.#selectedCategories.map(el => `text.${el}-label`).join(",");
            //for text that needs to slide down
            bars.selectAll(selectorText)
              .attr('display', 'block')
              .transition()
              .duration(this.#transitionDuration)
              .attr(y, function(d, i) {
                if (!proportional) {
                  let currentClass = d3.select(this).attr('class').split(" ")[1].replace("-label", "")
                  let currIndex = categories.indexOf(categoryReverseLookup[currentClass])
                  let subValue = calculateSubtractionValue(currIndex, removed, d)
                  return nScale(d[0][vertical ? last : first] - subValue - Math.abs(d[0][last] - d[0][first]) / 2);
                }
                else {
                  let identifiers = getRowIdentifiers(d);
                  let row = getRowInData(proportionalStack, identifiers, d)[0]
                  return nScale(row[vertical ? last : first] - Math.abs(row[last] - row[first]) / 2);
                }

              })
              .attr('opacity', function(d, i) {
                // d = proportional ? getRowInData(proportionalStack, d) : d
                if (proportional) {
                  let identifiers = getRowIdentifiers(d);
                  d = getRowInData(proportionalStack, identifiers, d)
                }
                let dimensions = that.#calculateTextDimensions(that.#getLabel(d[0][1] - d[0][0], proportional), that.#getFullFont(this))
                return that.#labelFitsStackedBar(dimensions.width, dimensions.height, nScale, d[0]) ? 1 : 0;
              })
              .tween("text", function(d, i) {
                if (proportional) {
                  let identifiers = getRowIdentifiers(d);
                  let row = getRowInData(proportionalStack, identifiers, d)[0]
                  // let row = d[0]
                  let selection = d3.select(this);
                  let oldVal = +selection.text().replace('%', '');
                  let newVal = row[1] - row[0]
                  const interpolate = d3.interpolate(+oldVal, newVal);
                  return function(t) {
                    selection.text(Math.round(interpolate(t)) + (proportional ? '%' : ''));
                  };
                }
              })
              .on('end', function(d, i) {
                let selection = d3.select(this);
                selection.attr('display', function(d) {
                  // d = proportional ? getRowInData(proportionalStack, d) : d
                  if (proportional) {
                    let identifiers = getRowIdentifiers(d);
                    d = getRowInData(proportionalStack, identifiers, d)
                  }
                  let dimensions = that.#calculateTextDimensions(that.#getLabel(d[0][1] - d[0][0], proportional), that.#getFullFont(this))
                  return that.#labelFitsStackedBar(dimensions.width, dimensions.height, nScale, d[0]) ? 'block' : 'none';
                })
              })
          }
        }
      }
    }

    let addBars = (classVal) => {
      this.#selectedCategories = this.#findSelectedValues()
      let subSeries = this.#selectedCategories.map(el => {
        return categoryReverseLookup[el]
      })
      this.#cSubScale = this.#cSubScale.domain(subSeries)
      if (this.#grouped) {
        //grouped
        let barGroups = bars.selectAll(".bar-group");
        //shift bars
        shiftSelectedGroupRect(barGroups)
        // shift bar labels
        if (barLabels) {
          shiftSelectedGroupLabels()
        }
        if (this.#displayUncertainties) {
          shiftSelectedGroupUncertainties()
        }
      }
      else {
        //stacked
        let removed = []
        let proportionalStack = proportional ? createNewProportionalData(this.#data, subSeries) : null;
        // console.log(proportionalStack)

        let notSelected = []
        this.#categories.map((el, i) => {
          let translatedEl = categoryLookup[el]
          if (!this.#selectedCategories.includes(translatedEl)) {
            notSelected.push(translatedEl)
          }
        })
        // console.log(this.#selectedCategories)
        if (notSelected.length != 0) {
          let notSelector = notSelected.map(el => `rect.${el}`).join(",");
          let rectGroups = bars.selectAll(notSelector)
          rectGroups.each(function(d, i) {
            // let currentClass = d3.select(this).attr('class')

            removed.push({
              "key": d.key,
              "data": d[0].data,
              "value": Math.abs(d[0][last] - d[0][first])
            })
          })
        }


        let selectorRect = this.#selectedCategories.map(el => `rect.${el}`).join(",");
        bars.selectAll(selectorRect)
          .transition()
          .duration(this.#transitionDuration)
          .attr(y, function(d, i) {
            if (!proportional) {
              let currentClass = d3.select(this).attr('class')
              let currIndex = categories.indexOf(categoryReverseLookup[currentClass])

              let subValue = calculateSubtractionValue(currIndex, removed, d)
              return nScale(d[0][last] - subValue);
            }
            else {
              let identifiers = getRowIdentifiers(d);
              let row = getRowInData(proportionalStack, identifiers, d)[0]
              return nScale(row[last]);
            }
          })
          .attr('opacity', 1)
          .attr(h, (d, i) => {
            if (!proportional) {
              let height = nScale(d[0][first]) - nScale(d[0][last]);
              return height == 0 || isNaN(height) ? 0.1 : height
            }
            else {
              let identifiers = getRowIdentifiers(d);
              let row = getRowInData(proportionalStack, identifiers, d)[0]
              let height = nScale(row[first]) - nScale(row[last]);
              return height == 0 || isNaN(height) ? 0.1 : height;
            }
          })

        if (barLabels) {
          let selectorText = this.#selectedCategories.map(el => `text.${el}-label`).join(",");
          bars.selectAll(selectorText)
            .attr('display', 'block')
            .transition()
            .duration(this.#transitionDuration)
            .attr(y, function(d, i) {
              if (!proportional) {
                let currentClass = d3.select(this).attr('class').split(" ")[1].replace("-label", "")
                let currIndex = categories.indexOf(categoryReverseLookup[currentClass])
                let subValue = calculateSubtractionValue(currIndex, removed, d)
                return nScale(d[0][vertical ? last : first] - subValue - Math.abs(d[0][last] - d[0][first]) / 2);
              }
              else {
                let identifiers = getRowIdentifiers(d);
                let row = getRowInData(proportionalStack, identifiers, d)[0]
                return nScale(row[vertical ? last : first] - Math.abs(row[last] - row[first]) / 2);
              }
            })
            .attr('opacity', function(d, i) {
              // d = proportional ? getRowInData(proportionalStack, d) : d
              if (proportional) {
                let identifiers = getRowIdentifiers(d);
                d = getRowInData(proportionalStack, identifiers, d)
              }
              let dimensions = that.#calculateTextDimensions(that.#getLabel(d[0][1] - d[0][0], proportional), that.#getFullFont(this))
              return that.#labelFitsStackedBar(dimensions.width, dimensions.height, nScale, d[0]) ? 1 : 0;
            })
            .tween("text", function(d, i) {
              // return d[1] - d[0] + (isProportionalLabel ? '%' : 0);
              if (proportional) {
                let identifiers = getRowIdentifiers(d);
                let row = getRowInData(proportionalStack, identifiers, d)[0]
                let selection = d3.select(this);
                let oldVal = +selection.text().replace('%', '');
                let newVal = row[1] - row[0]
                const interpolate = d3.interpolate(+oldVal, newVal);
                return function(t) {
                  selection.text(Math.round(interpolate(t)) + (proportional ? '%' : ''));
                };
              }
            })
            .on('end', function(d, i) {
              let selection = d3.select(this);
              selection.attr('display', function(d) {
                // d = proportional ? getRowInData(proportionalStack, d) : d
                if (proportional) {
                  let identifiers = getRowIdentifiers(d);
                  d = getRowInData(proportionalStack, identifiers, d)
                }
                let dimensions = that.#calculateTextDimensions(that.#getLabel(d[0][1] - d[0][0], proportional), that.#getFullFont(this))
                return that.#labelFitsStackedBar(dimensions.width, dimensions.height, nScale, d[0]) ? 'block' : 'none';
              })
            })
        }
      }
    }

    let updateNAxis = () => {
      //reinitialize all the nAxis variables to accomodate the removed bars, and update it
      this.initNScale(this.#log, false);

      this.initAxes();
      this.#updateAxes();

      //update local reference to the nScale
      nScale = this.#nScale;
    }

    let barClicked = (clickedClass) => {
      let circles = legend.selectAll('circle')

      if (!collapsed) {
        categoriesBeforeCollapse = this.#findSelectedValues()
        circles.each(function(d) {
          let circle = d3.select(this)
          let classVal = circle.attr("class").split(" ")[0]

          if (circle.classed("selected") && classVal != clickedClass) {
            fadeLegendCenter(classVal)
          }
        })
        if (!this.#interactiveFixedAxis) {
          updateNAxis()
        }
        removeBars()
        collapsed = true;
      }
      else {
        categoriesBeforeCollapse.map(el => {
          reverseFadeCenter(el)
        })
        if (!this.#interactiveFixedAxis) {
          updateNAxis()
        }
        addBars()
        collapsed = false;
      }
    }

    //for all bar-group rectangles (bars), react on click
    let barGroups = bars.selectAll('.bar-group')

    barGroups.selectAll("rect")
      .on('click', function(e, d) {
        if (that.#interactive) {
          let clicked = d3.select(this)
          let clickedClass = clicked.attr("class");

          barClicked(clickedClass)

          if (that.#callbackClick) {
            // console.log('bar.js click')
            that.#callbackClick(d)
          }
        }
      })
      .on('mouseover', function(e, d) {
        if (that.#interactive) {
          if (that.#callbackHover) {
            that.#callbackHover(d)
          }
          d3.select(this).attr('stroke', 'black')
        }
      })
      .on('mouseout', function(e, d) {
        if (that.#interactive) {
          d3.select(this).attr('stroke', null)
        }
      })
      .on('focus', (e, d) => {
        if (this.#interactive) {
          if (this.#callbackHover) {
            this.#callbackHover(d);
          }
        }
      })

    let legendClicked = (circleSelection) => {
      let last = false;
      selectedValues = this.#findSelectedValues();
      if (selectedValues.length <= 1) {
        last = true;
      }

      collapsed = false;
      let clicked = circleSelection // circleSelection
      let classVal = clicked.attr("class").split(" ")[0]

      if (clicked.classed("selected")) {
        if (last) {
          categories.filter(el => !selectedValues.includes(categoryLookup[el])).map(el => {
            reverseFadeCenter(categoryLookup[el])

          })
          if (!this.#interactiveFixedAxis) {
            updateNAxis()
          }
          addBars()
        }
        else {
          fadeLegendCenter(classVal)
          if (!this.#interactiveFixedAxis) {
            updateNAxis()
          }
          removeBars()
        }
      }
      else {
        reverseFadeCenter(classVal)
        if (!this.#interactiveFixedAxis) {
          updateNAxis()
        }
        addBars()
      }
    }

    //legend interaction
    legend.selectAll('circle')
      .on('click', (e, d) => {
        if (this.#interactive) {
          let selection = d3.select(e.target)
          // legendClicked(selection);
          if (this.#legendInteractionType == "toggle") {
            legendClicked(selection);
          }
          else if (this.#legendInteractionType == 'isolate') {
            barClicked(selection.attr('class').split(' ')[0]);
          }
        }
      });
    legend.selectAll('text')
      .on('click', (e, d) => {
        if (this.#interactive) {
          let clickedClass = d3.select(e.target).attr("class")
          let attachedCircle = legend.selectAll(`circle.${clickedClass}`)
          if (this.#legendInteractionType == "toggle") {
            legendClicked(attachedCircle);
          }
          else if (this.#legendInteractionType == 'isolate') {
            barClicked(clickedClass.split(' ')[0]);
          }
        }
      });

    legend.selectAll('g')
      .on('mouseover', (e, d) => {
        if (this.#interactive) {
          if (this.#callbackLegendHover) {
            this.#callbackLegendHover(d);
          }
        }
      })
      .on('focus', (e, d) => {
        if (this.#interactive) {
          if (this.#callbackLegendHover) {
            this.#callbackLegendHover(d);
          }
        }
      })
  }
  #renderLegend() {
    let that = this;
    if (!this.#legendGroup)
      this.#legendGroup = this.#container.append('g').attr('class', 'legend')
    const legend = this.#legendGroup

    // Save private fields (can't access 'this' when rendering items)
    const r = this.#legendRadius;
    const textOffset = this.#legendTextOffset;
    const circleSpacing = this.#legendCircleSpacing;
    const secondaryCircleSpacing = this.#legendSecondaryCircleSpacing;
    const spaceFromGraph = this.#legendSpacingFromGraph;
    const heightFromTop = this.#margins.t
    // console.log("legendPos", this.#l)
    const legendPosition = this.#legendPosition ?? [this.#width - this.#margins.l - this.#margins.r + spaceFromGraph, heightFromTop]

    const colourScale = this.#colourScale;

    const categoryLookup = this.#categoryLookup;
    const transitionDuration = this.#transitionDuration;

    legend.attr('display', this.#displayLegend ? "block" : "none")

    //dummy legend to get background size
    let dummyLegend = legend.append('g').attr('opacity', 0)

    dummyLegend
      .selectAll('g')
      .data(this.#categories)
      .join(
        (enter) => {
          let g = enter.append('g');

          let circle = g.append('circle')
            .attr('r', r)
            .attr('cx', (d, i) => legendPosition[0] + (this.#legendOrientation == 'v' ? 0 : circleSpacing * i))
            .attr('cy', (d, i) => legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0))

          let text = g.append('text')
            .attr('alignment-baseline', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('x', (d, i) => legendPosition[0] + textOffset + (this.#legendOrientation == 'v' ? 0 : (circleSpacing) * i))
            .attr('y', (d, i) => legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0))
          text.text(d => d)
        }
      )

    // background rectangle
    let legendBackground = legend.select(".background-rect").empty() ? legend.append('rect').attr('class', "background-rect") : legend.select(".background-rect")
    //change background rect position and size to fit text/rect/title
    let bounding = dummyLegend.node().getBBox();
    // console.log(bounding)
    let rectPadding = 5
    legendBackground
      .attr('opacity', 0.8)
      .attr('fill', 'white')
      .attr('rx', 10)
      .attr('ry', 10)
      .attr('x', bounding.x - rectPadding)
      .attr('y', bounding.y - rectPadding)
      .attr('width', bounding.width + rectPadding * 2)
      .attr('height', bounding.height + rectPadding * 2)

    let legendGroupBoundings = []
    if (this.#detectLegendSpacing) {
      dummyLegend.selectAll('g').each(function() {
        legendGroupBoundings.push(this.getBBox())
      })
      // console.log(legendGroupBoundings)
    }

    //remove the placeholder/dummy legend
    dummyLegend.remove()

    legend.selectAll('g.legend-group')
      .data(this.#categories)
      .join(
        (enter) => {
          let g = enter.append('g')
            .attr('class', 'legend-group')
            .attr('tabindex', -1);

          //circle
          let circle = g.append('circle')
            .attr('r', r)
            .attr('cx', (d, i) => {
              if (this.#legendItemWrapCounter) {
                return legendPosition[0] + (this.#legendOrientation == 'v' ? circleSpacing * Math.floor(i / this.#legendItemWrapCounter) : circleSpacing * (i % this.#legendItemWrapCounter))
              }
              else if (this.#detectLegendSpacing) {
                let spacing
                if (i == 0) {
                  spacing = 0;
                }
                else {
                  spacing = circleSpacing * i + legendGroupBoundings.filter((el, index) => index < i).reduce((partialSum, el) => partialSum + el.width, 0)
                }
                // console.log(spacing)
                return legendPosition[0] + (this.#legendOrientation == 'v' ? 0 : spacing)
              }
              return legendPosition[0] + (this.#legendOrientation == 'v' ? 0 : circleSpacing * i)

            })
            .attr('cy', (d, i) => {
              if (this.#legendItemWrapCounter) {
                return legendPosition[1] + (this.#legendOrientation == 'v' ? (circleSpacing * (i % this.#legendItemWrapCounter)) : (secondaryCircleSpacing * Math.floor(i / this.#legendItemWrapCounter)))
              }
              else
              if (this.#detectLegendSpacing) {
                return legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0)
              }
              return legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0)

            })
            .attr('class', d => categoryLookup[d])
            .attr('opacity', 0)
            .attr('fill-opacity', 0)
            .attr('fill', (d, i) => {
              let myColour = colourScale(d);
              if (this.#textures && this.#textureSeries[i] != 'solid') {
                return this.#textureSeries[i].url();
              }
              return myColour
            })
            .classed('selected', true)
            .transition()
            .duration(this.#transitionDuration)
            .attr('opacity', 1)
            .attr('fill-opacity', 1)

          //text
          let text = g.append('text')
            .attr('display', this.#hideLegendText ? "none" : "block")
            .attr('class', d => categoryLookup[d])
            .attr('alignment-baseline', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('x', (d, i) => {
              if (this.#legendItemWrapCounter) {
                return legendPosition[0] + textOffset + (this.#legendOrientation == 'v' ? circleSpacing * Math.floor(i / this.#legendItemWrapCounter) : circleSpacing * (i % this.#legendItemWrapCounter))
              }
              else if (this.#detectLegendSpacing) {
                let spacing
                if (i == 0) {
                  spacing = 0;
                }
                else {
                  spacing = circleSpacing * i + legendGroupBoundings.filter((el, index) => index < i).reduce((partialSum, el) => partialSum + el.width, 0)
                }
                return legendPosition[0] + textOffset + (this.#legendOrientation == 'v' ? 0 : spacing)
              }
              return legendPosition[0] + textOffset + (this.#legendOrientation == 'v' ? 0 : (circleSpacing) * i)
            })
            .attr('y', (d, i) => {
              if (this.#legendItemWrapCounter) {
                return legendPosition[1] + (this.#legendOrientation == 'v' ? (circleSpacing * (i % this.#legendItemWrapCounter)) : (secondaryCircleSpacing * Math.floor(i / this.#legendItemWrapCounter)))
              }
              return legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0)
            })
            .attr('opacity', 0)
            .transition()
            .duration(this.#transitionDuration)
            .attr('opacity', 1)

          text.text(d => d)
          // if (this.#interactive) {
          circle.attr('cursor', this.#interactive ? 'pointer' : 'auto')
          text.attr('cursor', this.#interactive ? 'pointer' : 'auto')
          // }
        },
        (update) => {
          //circle
          let circle = update.select('circle')
            .attr('class', d => categoryLookup[d])
            .classed('selected', true)
            // .attr('opacity', 0)
            .attr('opacity', function(d) {
              // console.log(d)
              let selection = d3.select(this.parentNode)
              // console.log(selection.text(), d)
              if (selection.text() == d) {
                return d3.select(this).attr('opacity')
              }
              return 0
            })
            .attr('fill-opacity', 1)
            .attr('fill', (d, i) => {
              let myColour = colourScale(d);
              if (this.#textures && this.#textureSeries[i] != 'solid') {
                return this.#textureSeries[i].url();
              }
              return myColour
            })
            .attr('r', r)
            .attr('cx', (d, i) => {
              if (this.#legendItemWrapCounter) {
                return legendPosition[0] + (this.#legendOrientation == 'v' ? circleSpacing * Math.floor(i / this.#legendItemWrapCounter) : circleSpacing * (i % this.#legendItemWrapCounter))
              }
              else if (this.#detectLegendSpacing) {
                let spacing
                if (i == 0) {
                  spacing = 0;
                }
                else {
                  spacing = circleSpacing * i + legendGroupBoundings.filter((el, index) => index < i).reduce((partialSum, el) => partialSum + el.width, 0)
                }
                // console.log(spacing)
                return legendPosition[0] + (this.#legendOrientation == 'v' ? 0 : spacing)
              }
              return legendPosition[0] + (this.#legendOrientation == 'v' ? 0 : circleSpacing * i)

            })
            .attr('cy', (d, i) => {
              if (this.#legendItemWrapCounter) {
                return legendPosition[1] + (this.#legendOrientation == 'v' ? (circleSpacing * (i % this.#legendItemWrapCounter)) : (secondaryCircleSpacing * Math.floor(i / this.#legendItemWrapCounter)))
              }
              else
              if (this.#detectLegendSpacing) {
                return legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0)
              }
              return legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0)

            })
            .transition().duration(this.#transitionDuration)
            .attr('opacity', 1)


          //text
          let text = update.select('text')
            .attr('class', function(d) {
              return categoryLookup[d];
            })
            .attr('opacity', function(d) {
              let selection = d3.select(this)
              if (selection.text() == d) {
                return selection.attr('opacity')
              }
              return 0
            })
            // .attr('opacity', 0)
            .attr('display', this.#hideLegendText ? "none" : "block")
            .text(d => d)

          text
            .attr('x', (d, i) => {
              if (this.#legendItemWrapCounter) {
                return legendPosition[0] + textOffset + (this.#legendOrientation == 'v' ? circleSpacing * Math.floor(i / this.#legendItemWrapCounter) : circleSpacing * (i % this.#legendItemWrapCounter))
              }
              else if (this.#detectLegendSpacing) {
                let spacing
                if (i == 0) {
                  spacing = 0;
                }
                else {
                  spacing = circleSpacing * i + legendGroupBoundings.filter((el, index) => index < i).reduce((partialSum, el) => partialSum + el.width, 0)
                }
                return legendPosition[0] + textOffset + (this.#legendOrientation == 'v' ? 0 : spacing)
              }
              return legendPosition[0] + textOffset + (this.#legendOrientation == 'v' ? 0 : (circleSpacing) * i)
            })
            .attr('y', (d, i) => {
              if (this.#legendItemWrapCounter) {
                return legendPosition[1] + (this.#legendOrientation == 'v' ? (circleSpacing * (i % this.#legendItemWrapCounter)) : (secondaryCircleSpacing * Math.floor(i / this.#legendItemWrapCounter)))
              }
              return legendPosition[1] + (this.#legendOrientation == 'v' ? circleSpacing * i : 0)
            })
            .transition()
            .duration(this.#transitionDuration)
            .attr('opacity', 1)


          // if (this.#interactive) {
          circle.attr('cursor', this.#interactive ? 'pointer' : 'auto')
          text.attr('cursor', this.#interactive ? 'pointer' : 'auto')
          // }
        },
        (exit) => {
          // exit.select('text')
          //   .transition()
          //   .duration(this.#transitionDuration)
          //   .attr('opacity', 0)

          // exit.select('circle')
          //   .transition()
          //   .duration(this.#transitionDuration)
          //   .attr('opacity', 0)
          //   .on('end', () => exit.remove())
          exit.remove()
        }
      )

    //add an html legend at the selection specified
    if (this.#htmlLegend) {
      //if more than one legend item, build the legend
      if (this.#htmlLegendHideSingle && this.#categories.length <= 1) {
        this.#htmlLegend.html("")
      }
      else {
        this.#htmlLegend.html("")
        this.#htmlLegend
          .style("list-style", "none")
          .style("text-align", "center")
          .style("line-height", "inherit")
          .style("text-wrap", "balance")

        this.#categories
          .forEach((text, i) => {
            //add legend item
            let li = this.#htmlLegend
              .append('li')
              .style("display", "inline-block")
              .style("margin-right", "15px")
              .style("margin-left", "15px")
              .style("text-align", "left")
              .classed(`val${i}`, true)

            //simulate the click, and the opacity
            // if (this.#interactive) {
            li.on('click', function() {
              if (that.#interactive) {
                legend.select(`text.val${i}`).dispatch('click')
                let selection = d3.select(this)
                let selected = selection.classed('selected')
                selection
                  .classed('selected', !selected)
                  .transition()
                  .duration(transitionDuration)
                  .style('opacity', selected ? 1 : 0.3)

              }
            })

            li.style('cursor', this.#interactive ? 'pointer' : 'auto')
            // }


            let div = li.append('div')
              .attr('class', 'listDiv')
              .style("display", "grid")
              .style("grid-template-columns", "30px auto")

            // div.append('span')
            //   .attr('class', 'legend-colour')
            //   .style('background-color', this.#colourScale(text))
            //   .style("border", "1px solid #ccc")
            //   .style("width", "20px")
            //   .style("height", "20px")
            //   .style("position", "relative")
            //   .style("top", "50%")
            //   .style("transform", "translate(0, -8px)")
            div.append('svg')
              .attr('width', "20px")
              .attr('height', "20px")
              .style("position", "relative")
              .style("top", "50%")
              .style("transform", "translate(0, -8px)")
              .append('rect')
              .attr('width', "20px")
              .attr('height', "20px")
              .attr('fill', (d, i) => {
                let myColour = colourScale(text);
                if (this.#textures && this.#textureSeries[i] != 'solid') {
                  return this.#textureSeries[i].url();
                }
                return myColour
              })

            div.append('span')
              .attr('class', 'legend-text')
              .text(text)
          })
      }
    }
  }
  #findSelectedValues() {
    let selectedValues = [];
    this.#legendGroup.selectAll(`circle.selected`).each(function(d) {
      let clicked = d3.select(this);
      if (d3.select(this).classed("selected")) {
        selectedValues.push(clicked.attr("class").split(" ")[0]);
      }
    })
    return selectedValues;
  }
  #setTabbing() {
    const container = this.#container;
    const bars = this.#container.select(".bars");
    const that = this;
    let layer = 0;

    container
      .on('keydown', (e) => {
        const isContainer = e.target.id == container.attr('id');
        //find which legend values are toggled on or off
        let selectedValues = this.#findSelectedValues();
        // console.log(e)
        let targetSelection = d3.select(e.target);

        if (e.key == 'Enter') {
          //begin inner tabbing between regions
          if (isContainer && selectedValues.length != 1) {
            //merge children bar groups and legend groups to set all the tabbing
            let children = bars.selectAll("g[data-layer='0']")
            let legendGroups = this.#legendGroup.selectAll('.legend-group')
            if (!children.empty()) {
              children
                .attr('tabindex', 0);
              children.node().focus(); //first child
              legendGroups
                .attr('tabindex', 0);

              // console.log('entered container')
            }
          }
          //dont remember, think the idea was that if there's a single rect available, go directly to it and skip the parent groups
          else if (isContainer && selectedValues.length == 1) {
            // console.log('how')
            let rects = bars.selectAll('rect')
              .filter(d => selectedValues.includes(this.#categoryLookup[this.#grouped ? d[this.#categoryKey] : d.key]))
            rects.attr('tabindex', 0)
            rects.node().focus();
            let legendGroups = this.#legendGroup.selectAll('.legend-group')
            legendGroups
              .attr('tabindex', 0);
          }
          //go deeper in grouping on enter
          else if (targetSelection.attr('class') == 'bar-group') {
            let dataLayer = parseInt(targetSelection.attr('data-layer'))
            if (dataLayer + 1 < this.#cSeries.length) {
              //select next bar-group child
              let nextBG = targetSelection.selectAll(`g[data-layer='${dataLayer + 1}']`)
              nextBG.attr('tabindex', 0)
              nextBG.node().focus();
            }
            else {
              //select first child rect
              //set all selectable rectangles tabindex
              let rects = targetSelection.selectAll('rect')
                .filter(d => selectedValues.includes(this.#categoryLookup[this.#grouped ? d[this.#categoryKey] : d.key]))
              rects.attr('tabindex', 0)
              rects.node().focus();
            }


          }
          // like you clicked a rect
          else {
            let selection = d3.select(e.target);
            // console.log('click from enter', e.target)
            //if it's the legend, act like it clicked the circle (didn't want to go rework the legend interactivity)
            if (selection.attr('class') == 'legend-group') {
              selection.select('circle').dispatch('click')
            }
            else {
              selection.dispatch('click')
            }

            //refind the selected values since they changed on click
            selectedValues = this.#findSelectedValues();

            //identify selectable and unselectable rectangles
            let barGroups = bars.selectAll('g');
            let rects = barGroups.selectAll('rect')
              .filter(d => selectedValues.includes(this.#categoryLookup[this.#grouped ? d.type : d.key]))

            let notSelectedRects = barGroups.selectAll('rect')
              .filter(d => !selectedValues.includes(this.#categoryLookup[this.#grouped ? d.type : d.key]))

            //set all tabindexes of selectable and unselectable rectangles
            rects.attr('tabindex', 0)
            notSelectedRects.attr('tabindex', -1)
            selectedValues.length == 1 ? barGroups.attr('tabindex', -1) : barGroups.attr('tabindex', 0)

          }

        }
        //get out of inner indexes, reset to svg
        else if (e.key == 'Escape') {
          bars.selectAll('g').attr('tabindex', -1);
          this.#legendGroup.selectAll('.legend-group').attr('tabindex', -1)
          container.node().focus();
          // console.log('escape')
        }

        //check where in dom. If leaving graph, hide indexes from order.
        else if (e.key == "Tab") {
          // console.log(e)
          let barGroups = bars.selectAll('g');
          let rects = bars.selectAll('rect');
          let legendGroups = this.#legendGroup.selectAll('.legend-group');

          let barArrOfArr = [];
          // let barArr = Array.from(barGroups._groups[0])
          let barArr = [...barGroups, ...legendGroups]
          let legendArr = [...legendGroups]
          this.#cSeries.map((c, i) => {
            barArrOfArr.push(bars.selectAll(`g[data-layer='${i}']`))
          })
          // console.log("tablayers", barArrOfArr)
          // console.log(barArr)
          let rectArr = Array.from(rects._groups[0])

          let barIndex = barArr.indexOf(e.target)
          let rectIndex = rectArr.indexOf(e.target)
          let legendIndex = legendArr.indexOf(e.target)

          // console.log('barIndex', barIndex, 'legendIndex', legendIndex)

          //this chunk controls the tab indexing when moving between group and rect, need to extend between group layers
          if (barIndex != -1 || legendIndex != -1) {
            // console.log('isBarOrLegend')
            //if in a bargroup, not looking at rects
            rects.attr('tabindex', -1)

            //if in a bargroup, turn off the bargroups below it. This makes it so that when you pop out of a subgroup after tabbing through it all, it gets removed from taborder again
            let dataLayer = parseInt(d3.select(e.target).attr('data-layer'));
            this.#cSeries.map((c, i) => {
              if (i > dataLayer) {
                barArrOfArr[i].attr('tabindex', -1)
              }
            })

            //if leaving all the bargroups in either min/max, turn off the bargroups
            if (!e.shiftKey && barIndex == barArr.length - 1) {
              // console.log("leave bar forwards")
              barGroups.attr('tabindex', -1)
            }
            else if (e.shiftKey && barIndex == 0) {
              // console.log("leave bar backwards")
              barGroups.attr('tabindex', -1)
            }
          }
          else if (!e.shiftKey && rectIndex != -1 && rectIndex == rectArr.length - 1) {
            // console.log('is rect')
            rects.attr('tabindex', -1)
            barGroups.attr('tabindex', -1)
          }
        }
      })
      // //sets indexing for clicked item before the 'onclick event' of a bar
      .on('mousedown', (e) => {
        let selectedValues = this.#findSelectedValues();
        // console.log('mousedown', selectedValues)
        let barGroups = bars.selectAll('g');
        let rects = bars.selectAll('rect');

        let barArr = Array.from(barGroups._groups[0])
        let rectArr = Array.from(rects._groups[0])
        let jointGroups = barArr.concat(rectArr)

        //check if any of the outlined groups contain the target. focus it if it is
        if (jointGroups.includes(e.target)) {
          //check which specific group it belongs to and set the indexing accordingly for that specific entry
          if (rectArr.includes(e.target)) {
            d3.select(e.target).attr('tabindex', 0)
            barGroups.attr('tabindex', 0)
          }
          else if (barArr.includes(e.target)) {
            // rects.attr('tabindex', -1)
            barGroups.attr('tabindex', 0)
          }
        }
      })
      //sets indexing for other rect after the 'onclick event' of a bar
      .on('click', (e) => {
        //find which legend values are toggled on or off
        let selectedValues = this.#findSelectedValues();

        // console.log(e.target)

        //set all selectable rectangles tabindex
        // let rects = d3.select(e.target.parentNode).selectAll('rect')
        let rects = bars.selectAll('rect')
          .filter(d => {
            return selectedValues.includes(this.#categoryLookup[this.#grouped ? d.type : d.key])
          })

        // console.log('rects', rects)

        let barGroups = bars.selectAll('g');
        let legendGroups = this.#legendGroup.selectAll('.legend-group');


        let barArr = Array.from(barGroups._groups[0])
        let rectArr = Array.from(rects._groups[0])
        let legendArr = [...legendGroups]
        let jointGroups = [...barGroups, ...rects, ...legendGroups]

        let legendClicked = legendArr.includes(e.target.parentNode);

        // console.log(legendClicked);

        //check if any of the outlined groups contain the target. focus it if it is
        if (jointGroups.includes(e.target) || legendClicked) {
          legendGroups.attr('tabindex', 0)
          //check which specific group it belongs to and set the indexing accordingly
          if (rectArr.includes(e.target)) {
            bars.selectAll('rect').attr('tabindex', -1)
            rects.attr('tabindex', 0)
            selectedValues.length == 1 ? barGroups.attr('tabindex', -1) : barGroups.attr('tabindex', 0)
            e.target.focus()
          }
          else if (barArr.includes(e.target)) {
            barGroups.attr('tabindex', 0)
            e.target.focus()
          }
          else if (legendClicked) {
            barGroups.attr('tabindex', 0)
            e.target.parentNode.focus()
          }

        }
        else {
          // console.log('target not in joint')
        }
      })
      .on('focusout', function(e) {
        // console.log('focusout', e)
        let barGroups = bars.selectAll('g');
        let rects = bars.selectAll('rect');
        let legendGroups = that.#legendGroup.selectAll('.legend-group');

        // let jointGroups = Array.from(barGroups._groups[0]) //bar groups
        //   .concat(Array.from(rects._groups[0])) //rect

        let jointGroups = [...barGroups, ...rects, ...legendGroups]

        if (!jointGroups.includes(e.relatedTarget)) {
          rects.attr('tabindex', -1)
          barGroups.attr('tabindex', -1)
          legendGroups.attr('tabindex', -1)
        }
      })
  }
  #renderTooltips() {
    /*
    This function adds a tooltip box to the graph's wrapper
    and returns event handlers needed to control it.
    
    Parameters
    ---------------------
    undefined
    
    Returns
    ---------------------
    array
    - An array of three functions that handle the following events:
      onMouseEnter, onMouseLeave, and onMouseMove
    - These event handlers are meant to be added to the graph's bars.
    */

    const colourScale = this.#colourScale;
    const categories = this.#categories;
    const cSeries = this.#cSeries;
    const cSeriesLast = this.#cSeries[this.#cSeries.length - 1]

    const tooltipSeries = this.#tooltipSeries ?
      this.#tooltipSeries : [cSeriesLast, ...this.#categories];

    const proportional = this.#proportional;

    // Create tooltip element
    const tooltip = this.#wrapper.select(".tooltip").empty() ?
      this.#wrapper
      .append('div')
      .attr('class', 'tooltip')
      .attr('opacity', 0) :
      this.#wrapper.select(".tooltip")



    const categoryLookup = this.#categoryLookup;
    const categoryReverseLookup = this.#categoryReverseLookup;
    let cKeys = this.#cKeys;

    let findRow = (data, cKey, nKey) => {
      let row = data.find(el => el.key == cKey)
      return row.find(el => el.key == nKey);
    }

    let orientations = ['tr', 'br', 'bl', 'tl']

    // Create event handlers
    let onEnter = (e, d) => {
      if (!Object.keys(d).includes('data')) d.data = d;

      const selectedCategories = this.#findSelectedValues();
      const subSeries = selectedCategories.map(el => categoryReverseLookup[el])
      const proportionalStack = this.#proportionalStack;
      const stackData = this.#stackData;

      // Get series
      let html = '';
      let key = d[this.#categoryKey] ?? d.key;

      if (this.#tooltipFunction) {
        html = this.#tooltipFunction(d, colourScale(key))
      }
      else {
        let spanAttr = `style="border-left:5px solid ${colourScale(key)}; padding-left:3px"`
        let value = this.#grouped ? this.#getLabel(d[this.#nKey], proportional) : this.#getLabel(d[0][1] - d[0][0], proportional);
        html += `<div ${spanAttr}>${value} </div>`;
      }

      tooltip
        .html(html)
        .attr('data-orientation', orientations[1])
        .style('opacity', 1)
        .style("display", "block")
    }

    function onLeave(e, d) {
      tooltip
        .style('opacity', 0)
        .style("display", "none")
    }

    function onMove(e, d) {
      let gap = 25;

      let xPos = e.clientX;
      let yPos = e.clientY;

      tooltip
        .style("transform", `translateX(${gap}px)`)
        .style("left", `${xPos}px`)
        .style("top", `${yPos}px`)
    }


    return [onEnter, onLeave, onMove];
  }
  #addTable() {
    let data = this.#data;
    // console.log('tableData', this.#data)
    /*
      Adds a table to the #table property. Contains the standard classes typically used on infobase products.
      
      Note: uses #table, #tableSummary, #tableDetails, #data, #cSeries, #categories
    */

    const tableExists = !this.#table.select('details').empty();

    let tableDetails;

    if (tableExists) {
      this.#table.select('details').selectAll("*").remove();
      tableDetails = this.#table.select('details');
    }
    else {
      tableDetails = this.#table.append('details');
    }

    // let tableID = this.#table.attr('id') + "-table";


    tableDetails.append("summary").text(this.#tableSummary)

    // visual caption
    if (this.#tableCaption && this.#captionAbove)
      tableDetails.append('p')
      .attr('aria-hidden', true)
      .attr('class', 'caption')
      .text(this.#tableCaption)

    const tableContainer = tableDetails.append("div").attr("class", "table-responsive")
    const table = tableContainer.append("table")
      // .attr('id', tableID)
      .attr("class", "wb-table table table-bordered table-striped table-hover")

    if (this.#tableCaption) {
      let caption = table.append('caption')
        .text(this.#tableCaption)

      caption.classed('wb-inv', this.#captionAbove)
    }

    const tr = table.append('thead').append('tr').attr('class', 'bg-primary')
    // let tableArr = this.#data.columns;
    let tableArr = [...this.#cSeries]
    if (this.#categoryKey) {
      tableArr.push(this.#categoryKey)
    }
    tableArr.push(this.#nKey)
    if (this.#displayUncertainties) {
      tableArr.push(this.#upperUncertainty)
      tableArr.push(this.#lowerUncertainty)
    }
    // tableArr.push(this.#cKey)
    // tableArr = tableArr.concat(this.#categories)

    tableArr.map(el => {
      tr.append('th')
        // .style("vertical-align", "top").attr('scope', 'col')
        .text(() => {
          return this.#tableHeaderFunction ? this.#tableHeaderFunction(el) : el
        })
    })

    const tbody = table.append("tbody")

    let language = d3.select('html').attr('lang');

    this.#data.map(row => {
      let tr = tbody.append("tr")

      tableArr.map(el => {
        tr.append('td')
          .attr('data-sort', () => {
            let text = row[el]
            let number = parseFloat(text)
            if (!isNaN(number)) {
              return number
            }
          })
          .html(() => { //security would be better as .text, but want to be able to insert html
            let text = row[el]
            if (this.#tableCellFunction) {
              text = this.#tableCellFunction(text, row, el)
            }
            else if (!isNaN(text)) {
              let value = parseFloat(text)
              if (!isNaN(this.#decimalPlaces)) {
                value = this.#round(value)
                if (this.#decimalType == "fixed" && this.#decimalPlaces) {
                  value = value.toFixed(this.#decimalPlaces)

                }
                // console.log(value, this.#decimalPlaces)
              }

              return language == 'fr' ? (value + "").replace('.', ',') : value;
              // return value
            }

            return text
          })
      })
    })
    // console.log("---------", table)
    // $('#' + tableID).DataTable();

    let tableOrder;
    if (this.#tableOrder) {
      tableOrder = this.#tableOrder;
    }
    else {
      tableOrder = [0, 'asc'];
      // tableArr.map((el, i) => {tableOrder.push([i, 'asc'])})
    }


    if (language == 'en') {
      $(table.node()).DataTable({
        "order": tableOrder
      });
    }
    else {
      $(table.node()).DataTable({
        "order": tableOrder,
        "language": {
          "sProcessing": "Traitement en cours...",
          "sSearch": "Rechercher&nbsp;:",
          "sLengthMenu": "Afficher _MENU_ &eacute;l&eacute;ments",
          "sInfo": "Affichage de l'&eacute;lement _START_ &agrave; _END_ sur _TOTAL_ &eacute;l&eacute;ments",
          "sInfoEmpty": "Affichage de l'&eacute;lement 0 &agrave; 0 sur 0 &eacute;l&eacute;ments",
          "sInfoFiltered": "(filtr&eacute; de _MAX_ &eacute;l&eacute;ments au total)",
          "sInfoPostFix": "",
          "sLoadingRecords": "Chargement en cours...",
          "sZeroRecords": "Aucun &eacute;l&eacute;ment &agrave; afficher",
          "sEmptyTable": "Aucune donn&eacute;e disponible dans le tableau",
          "oPaginate": {
            "sFirst": "Premier",
            "sPrevious": "Pr&eacute;c&eacute;dent",
            "sNext": "Suivant",
            "sLast": "Dernier"
          },
          "oAria": {
            "sSortAscending": ": activer pour trier la colonne par ordre croissant",
            "sSortDescending": ": activer pour trier la colonne par ordre d&eacute;croissant"
          }
        },
      });
      table.on('click', 'th', function() {
        let tableID = table.attr('id');
        $("#" + table.attr('id') + " th").addClass("sorting")
        //$(this).removeClass("sorting")
      });
    }

    // $('#' + tableID).trigger("wb-init.wb-tables")
    // $( ".wb-tables" ).trigger( "wb-init.wb-tables" );
  }
  #dataMinMax(updateCalled) {
    /* gets min and max values in selected dataset */

    let min, max;

    const categoryReverseLookup = this.#categoryReverseLookup;
    let selectedKeys;

    if (updateCalled) {
      selectedKeys = this.#categories;
    }
    else {
      selectedKeys = this.#findSelectedValues().map(el => categoryReverseLookup[el])
      selectedKeys = selectedKeys.length === 0 ? this.#categories : selectedKeys;
    }

    // computes min max across stack data
    if (!this.#grouped) {
      // console.log('groupData', this.#groupData)
      // console.log('stackData', this.#stackData)
      
      
      //TODO: NEED TO CHECK WHICH GROUPS ARE SELECTED AS WELL
      //arr to store sums
      let sumPerStack = [];
      let getSums = (d, depth) => {
        //if we're at the end of the rollup, get sum
        if (depth <= 1){
          //make array to store numbers to sum
          let arrToSum = []
          d[1].map(el => {
            let num = el[this.#nKey];
            //if the value is a number and is selected, add it to the sum array
            if (!isNaN(num) && selectedKeys.includes(el[this.#categoryKey])){
              arrToSum.push(Number(el[this.#nKey]))
            }
          })
          //sum it
          let sum = arrToSum.reduce((partialSum, a) => partialSum + a, 0)
          //add it to array of sums
          sumPerStack.push(sum)
        } 
        //else go one layer further for each piece of data
        else {
          d[1].map(newD => {
            getSums(newD, depth - 1)
          })
        }
      }
      this.#groupData.map(d => {
        getSums(d, this.#cSeries.length)
      })

      //find/sum local (one bar) min/max, compare against global (all bars) min/max. replace as logical
      // this.#stackData.map((el, i) => {
      //   let thisMin;
      //   let thisMax;

      //   el.map(rectData => {

      //     thisMin = thisMin ? (rectData[0] < thisMin ? rectData[0] : thisMin) : rectData[0];
      //     if (selectedKeys.includes(rectData.key)) {
      //       thisMax = thisMax ? (thisMax + rectData[1] - rectData[0]) : rectData[1] - rectData[0];
      //     }
      //   })
      //   if (!min) {
      //     min = thisMin
      //   }
      //   else {
      //     min = thisMin < min ? thisMin : min;
      //   }
      //   if (!max) {
      //     max = thisMax
      //   }
      //   else {
      //     max = thisMax > max ? thisMax : max;
      //   }
      // })
      
      
      

      // let cmp = function(a, b) {
      //   if (a > b) return +1;
      //   if (a < b) return -1;
      //   return 0;
      // }
      // let sortedData = structuredClone(this.#data).sort((a, b) => {
      //   let compareArr = []
      //   this.#cSeries.map(c => {
      //     compareArr.push(cmp(a[c], b[c]))
      //   })
      //   let result;
      //   compareArr.map(el => {
      //     if (!result) {
      //       result = el
      //     }
      //     else {
      //       result = result || el;
      //     }
      //   })
      //   // console.log(result, compareArr[0] || compareArr[1])
      //   return result;
      // })
      
      // // console.log('sortedData', sortedData)

      
      // // let lastCKey = this.#cSeries[this.#cSeries.length -1]
      // // console.log(this.#data.sort((a,b) => a[lastCKey] - b[lastCKey]))
      // // console.log('stackData', this.#stackData)
      
      // sortedData.map((el, i) => {

      //   if (selectedKeys.includes(el[this.#categoryKey])) {
      //     let index = parseInt(i / this.#categories.length)
      //     // console.log(index, el[this.#nKey])
      //     if (!sumPerStack[index]) {
      //       sumPerStack[index] = 0.0;
      //     }
      //     let value = isNaN(el[this.#nKey]) ? 0 : Number(el[this.#nKey])
      //     sumPerStack[index] = Number(sumPerStack[index] + value)

      //     // max = max ? (currMax > max ? currMax : max) : currMax

      //     // min = min ? (curr < min ? curr : min) : curr
      //   }
      // })
      
      // console.log(sumPerStack)
      min = d3.min(sumPerStack)
      max = d3.max(sumPerStack)
    }

    // computes min max across raw data
    else {
      this.#data.map(el => {
        if (selectedKeys.includes(el[this.#categoryKey])) {
          let curr = +el[this.#nKey]
          let currMax = curr;
          if (this.#displayUncertainties && +el[this.#upperUncertainty]) {
            currMax = curr > +el[this.#upperUncertainty] ? curr : +el[this.#upperUncertainty]
          }
          max = max ? (currMax > max ? currMax : max) : currMax

          min = min ? (curr < min ? curr : min) : curr
        }
      })
    }

    return [min, max];
  }
  #wrap(text, width) {
    let that = this;
    let splitRegex = /\s+/;

    text.each(function() {
      var text = d3.select(this),
        words = text.text().trim().split(splitRegex).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        x = text.attr("x") ?? 0,
        y = text.attr("y") ?? 0,
        dy = parseFloat(text.attr("dy")) ?? 0,
        tspan = text
        .text(null)
        .append("tspan")
        .attr("x", x)
        .attr("y", y)
        .attr("dy", dy + "em");

      //loop through the words and add them to a tspan
      while ((word = words.pop())) {
        line.push(word)
        let lineJoin = line.join(" ")
        tspan.text(lineJoin) // make array a sentence based on last split. If only one word in line array, then stays one word

        //if sentence is now too big for width, you've added too many words / word itself is too large. Modify to be under the width then render the tspan
        if (tspan.node().getComputedTextLength() > width) {
          //means the word alone is too long, so modify the font size until it fits. remove / modify this section if we don't want text shrinking
          if (line.length <= 1) {
            let fontSize = parseFloat(window.getComputedStyle(tspan.node(), null)["fontSize"])
            //go down a font-size until it fits
            while (tspan.node().getComputedTextLength() > width && fontSize > 0) {
              fontSize = parseFloat(window.getComputedStyle(tspan.node(), null)["fontSize"]);
              tspan.attr('font-size', `${fontSize - 1}px`)
            }
            text.selectAll('tspan').attr('font-size', `${fontSize - 1}px`)
            text.attr('font-size', `${fontSize - 1}px`)
          }
          //else there's a sentence. Make the sentence shorter by putting the last word of the line back on the word list
          else {
            words.push(line.pop());
            lineJoin = line.join(" ")
            tspan.text(lineJoin);
          }
          //make the next tspan if there are still words left and reset whats in a line
          if (words.length != 0) {
            tspan = text
              .append("tspan")
              .attr('font-size', text.attr('font-size')) // remove if we don't want text shrinking. gets font-size from parent text element if it exists
              .attr("x", x)
              .attr("y", y)
              .attr("dy", ++lineNumber * lineHeight + dy + "em")

            line = []
          }

        }
        //if there are no more words to loop through, then render the last joined words
        if (words.length == 0) {
          tspan
            .text(lineJoin);
        }
      }
    });
  }
  #fitToConstraints(text, constraint, that) {
    /* center tick titles, and shrink font-size if it extends beyond bounds */
    text.each(function() {
      let text = d3.select(this);
      let tspans = text.selectAll('tspan')
      let bounds = this.getBBox()
      // console.log(bounds, this.getBBox())
      let size = that.#vertical ? bounds.height : bounds.width;
      let fontSize = parseFloat(window.getComputedStyle(tspans.node(), null)["fontSize"]);
      // console.log(text.text())
      // console.log(size, constraint)
      while (size > constraint) {

        fontSize = parseFloat(window.getComputedStyle(tspans.node(), null)["fontSize"]) - 1;
        tspans.attr('font-size', `${fontSize}px`)

        bounds = this.getBBox()
        size = that.#vertical ? bounds.width : bounds.height;
        // console.log(size, constraint)
      }
      bounds = this.getBBox()
      size = that.#vertical ? bounds.width : bounds.height;
      text.attr('font-size', `${fontSize}px`)
      if (!that.#vertical) {
        let lineCount = tspans.size()
        text.attr("transform", `translate(0,${-size/2 + fontSize/2})`)
      }
    })
  }
  //#endregion
}
"""
        documentation = """## BarGraph Class

The aim of this class is to quickly create 
reusable bar graphs. Your job is to just send 
in the right data and style the graph with built in parameters or custom CSS.

### Quickstart

First, create an `index.html` file and `main.js` 
file. For this example, they are made in the same directory. 
- For the HTML file, ensure 
  you have a div whose only child is an SVG element.
- Also **ensure that you load the `d3.js` v7 library 
  and `main.js` as a module** (in that order).
- `main.js` represents YOUR js file that you wish to use the modules in.
- Example:

```
(index.html)
--------------------
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bar chart</title>
    <link href="/src/css/modular/main.css" rel="stylesheet" type="text/css">
</head>
<body>
<body>
  <figure>
    <figcaption class="h3">Figure title</figcaption>
    <div id='wrapper1'>
      <svg id='bar1'></svg>
    </div>
  </figure>
</body>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="/src/js/functions/localization.js"></script>
<script src='./main.js' type='module'></script>

</html>
```

Next, import `BarGraph` from `bar.js` in `main.js`. 
Can use this code as an example in `main.js` to 
set the basics for the graph.

```
(main.js)
---------------------
import { BarGraph } from "/src/js/modular/Updating/bar.js";

```

Now, add some more code to `main.js` to load the data you want.

**Example data format**
```
YEAR,VALUE,PT
2017,472.539,AB
2018,451.605,AB
2019,408.184,AB
2020,337.221,AB
2021,331.267,AB
2022,347.431,AB
2017,604.893,BC
2018,576.586,BC
2019,501.259,BC
2020,411.774,BC
2021,405.486,BC
2022,426.259,BC
2017,931.953,MB
2018,957.686,MB
2019,725.151,MB
2020,725.319,MB
2021,534.909,MB
2022,606.586,MB
```


Read in your data. This is one example of how to do it,
which lets you read in multiple csv and json files at once.

```
(main.js)
---------------------
// Load data, datafiles can contain multiple
let dataFiles = [
    '/src/data/yourProject/YOURDATAHERE.csv', // 0
]
let promises = [];
dataFiles.forEach(function(url) {
    if (url.match(/.*\.csv$/gm)) {
        promises.push(d3.csv(url))
    }
    else if (url.match(/.*\.json$/gm)) {
        promises.push(d3.json(url))
    }
});
Promise.all(promises).then(function(values) {
    console.log('myData', values) // values is an array of the data you loaded in.
    
    // Data is done being read in. Let's give it to a function to build it.
    buildBarchart(values[0])
})
```

Time to make a barchart! We'll set this up in it's own function that we referenced earlier.

```
(main.js)
---------------------
function buildBarchart(data){
  
    // Setup, table not required. Margins 
    const Bar = new BarGraph();
    Bar
      .wrapper(d3.select('div#wrapper1'))
      .container(d3.select('svg#bar1'))
      .table(d3.select('div#wrapper1'))
      .margins([60, 60, 100, 100])
    
    //set data and keys within it
      .data(data)
    //Categorical series, column(s) in data that contains the independant variables (xAxis when vertical). 
      .cSeries(['YEAR']) // for a nested cAxis, add more column names.
    // Numerical key. Represents the "y" or dependent variable
      .nKey('VALUE')
      
      .categoryKey('PT') // Seperation in the grouped/stacked bars. What will be shown in the legend.
    
    // Set titles as needed, all optional
      .graphTitle('Graph title') //would recommend using a figcaption instead
      .nAxisTitle('nAxis')
      .cAxisTitle('cAxis')
      
    // Set different boolean options. More options below
      .displayLegend(true)
      .grouped(true) // if false, is stacked
      
    // Legend options, more customization below
      .legendPosition([400, 50])
    
    // Initiliase scales, axes, generators, etc. Init and render are seperate calls incase an override of initialized variables is desired before render.
      .init()
    
    // Generate Bars
      .render();
}
```

You should now see a bar graph when you launch `index.html`.

A common use case is for graphs is to update display. To do so, simply change any desired parameters, and call update().
**Note: Some options do not remove on update, such as interactivity.** 
`Attempting to do so will cause bugs`
Example:

```
(main.js)
---------------------
function updateBarchart(newData){
  Bar
  .data(newData)
  .cSeries(['region'])
  .nKey('value')
  .categoryKey('cat')
  .graphTitle('Region stats')
  .nAxisTitle('Stats')
  .cAxisTitle('Region')
  .grouped(false)
  .colourSeries(['blue', 'red', 'yellow', 'purple', 'pink'])
  .init()
  .update();
}

```

## CSS

The barchart within the container is setup with classes. Use the inspector to see the format, 
but common uses are:
- *Bars*: `svg#bar1 g.bars` contains a subgroup for each series of data
  you have. For instance, it may contain `g.val0` and `g.val1`
  (if you set those values in your ySeries array). Each of these subgroups 
  will have `rect` elements whose fill you can change. 
- *Titles*: `svg#bar1 g.titles` contains three text elements 
  which represent the graph title (`text.graph-title`), 
  y-axis title (`text.n-axis-title`), and x-axis title 
  (`text.c-axis-title`).
- *Axes*: `svg#bar1>g.axes>g.y text` - all the text in the 
  y-axis. Similarly, `svg#bar1>g.axes>g.x text` selects 
  all the text in the x-axis.
- *Legend*: `svg#bar1>g.legend` contains a `circle` and `text` element
  per output series that you have. Each will have a class based on 
  the values you set in your ySeries array. Ex: You might have 
  elements like `text.var0` and `circle.var1`.
- *Tooltip*: `div#wrapper1>div.tooltip` is the tooltip element. You
  will likely want to change its size, background colour, etc. 


## Additional methods and attributes

**A better way to change the legend and bar colours** would be to set the Bar.colourSeries to a new array of desired colours.
 - `Bar.colourSeries(['blue', 'red', 'yellow'])`
This assigns the colours in order, such that `val0` is coloured `blue`, `val1` is coloured `red`, etc.

There are many other common ways to customize the bar graph listed below. These boolean values control whether that functionality appears, but are defaulted to false (mostly):
 - *Vertical*: `Bar.vertical(true);`
 - *Grouped*: `Bar.grouped(true);`
 - *Bar labels*: `Bar.barLabels(true);`
    - `alwaysDisplayBarLabels(true)` to always display them.
 - *Tooltips*: `tooltips(true);`
    - Requires the tooltip css to display properly. Is in the `src/css/modular/main.css` linked earlier
 - *Interactive*: `Bar.interactive(true);`
 - *Gridlines*: `Bar.gridlines(true);`
 - *Logarithmic scale*: `Bar.log(true);`
    - Only affects grouped bar charts
 - *Proportional*: `Bar.proportional(true);`
    - Only affects stacked bar charts
 - *Display legend*: `Bar.displayLegend(true);`
 - *Hide legend text*: `Bar.hideLegendText(true);`
 - *detectLegendSpacing*: `Bar.detectLegendSpacing(true);`
    - Spaces legend groups out when they are placed horizontally
 - *Display uncertainties*: `Bar.displayUncertainties(true);`
    - upperUncertainty and lowerUncertainty must also be set
 - *Percent*: `Bar.percent(true);`
    - This isn't for formatting percent values on the numerical axis. See `nTickFormat()``
 - *Wrap cAxis tick text*: `Bar.fitTickText(true);`
 - *Table caption above*: `Bar.captionAbove(true);`
 - *Legend hover fade*: `Bar.legendHoverFade(true);`
 - *textures*: `Bar.textures(true);`
    - Must load `<script src="/src/js/textures.js"></script>` before `main.js` to use

Customize the spacing, size and bar padding:
 - *Height*: `Bar.height(480);`
 - *Width*: `Bar.width(720);`
    - Width of the SVG will always be 100% of the container. The height and width attributes are the viewbox ratio of the SVG.
 - *Margins [Top, right, bottom, left]*: `Bar.margins([80,40,120,100]);`
 - *Padding between bar groups*: `Bar.cPaddingSeries([0.25]);`
    - One array element for each value in the cSeries
 - *Sub padding for grouped bar charts only*: `Bar.subPadding(0.25);`
 - *default padding for all padding values*: `Bar.defaultPadding(0.25);`
 - *c-Axis-title distance from axis*: `Bar.cAxisTitleSpacing(50);`
 - *n-Axis-title distance from axis*: `Bar.nAxisTitleSpacing(60);`

Customize the legend:
 - *Radius*: `Bar.legendRadius(6);`
 - *Horizontal space between circle and text*: `Bar.legendTextOffset(15);`
 - *Vertical space between vertical circles*: `Bar.legendCircleSpacing(15);`
 - *Horizontal space between graph and legend*: `Bar.legendSpacingFromGraph(30);`
 - *legendPosition*: `Bar.legendPosition([x, y]);`
    - Overwrites the spacing from graph, where x and y are the horizontal and vertical pixel position.
 - *legendOrientation*: `Bar.legendOrientation('v');`
    - accepts `h` or `v` for horizontal or vertical
 - *legendItemWrapCounter*: `Bar.legendItemWrapCounter(4);`
    - For horizontal legend. How many legend items until it wraps to new line. Niche use, not great in it's current form
 -  *legendInteractionType*: `Bar.legendInteractionType('isolate');`
    - Accepts either 'toggle' or 'isolate' for when you click the legend. Toggle removes that group from the graph selection, isolate removes everything else.
 - *detectLegendSpacing*: `Bar.detectLegendSpacing(true);`
    - Spaces legend groups out when they are placed horizontally

Adding textures:
 - *Textures*: `Bar.textures(true);`
    - Must load `<script src="/src/js/textures.js"></script>` before `main.js` to use
 - *Texture patterns*: `Bar.textureTypeSeries(["dots", "solid", "grid", "diagonal"])`
    - Determines the order in which the textures will display. Repeats across the colours in the given pattern.
    - Currently only accepts `dots`, `solid`, `grid`, `diagonal`. Easy to add more, feel free to request them.

Uncertainty lines (only for grouped barcharts):
 - *Upper uncertainty*: `Bar.upperUncertainty('upperKey');`
    - Key of the column name contianing the value for the upper uncertainty
 - *Lower uncertainty*: `Bar.lowerUncertainty('lowerKey');`
    - Key of the column name containing the value for the lower uncertainty
 - *Uncertainty width (pixels)*: `Bar.uncertaintyWidth(8);`

Average lines (bit rough)
 - *Average lines*: `Bar.averageLines([20, 10, 5])`
 - *Average lines colours*: `Bar.averageLinesColours(["black", "red", "orange"])`
 - *Average lines Type*: `Bar.averageLinesType(["solid", "dashed", "dashed"])`
    - Can be `solid`, `dashed`, or `dotted`
 - *Average lines*: `Bar.averageLinesLegendText(["Twenty", "Ten", "Five"])`
    - Replaces the number value with a text value at the same index
 
Customize formatting/misc.:
 - *How many decimals to round off to*: `Bar.decimalPlaces(1)`. Also call `.decimalType('fixed')` if using
 - *Transition duration*: `Bar.transitionDuration(1000)`
 - *Decimal type*: `Bar.decimalType('fixed')`
    - Can be `fixed` or `round`

Formatting functions *yourFormattingFunction referenced below* (overwrites any other formatting that would be handled by the code):
 - *tableHeaderFunction*: `Bar.tableHeaderFunction(yourFormattingFunction)`
    - `d`: The value of the raw table header
    - `return`: The value you want to display in its stead
 - *tableCellFunction*: `Bar.tableCellFunction(yourFormattingFunction)`
    - `d`: The value of the raw table cell
    - `return`: The value you want to display in its stead. Can be html
 - *tooltipFunction*: `Bar.tooltipFunction(yourFormattingFunction)`
    - `d`: The data of the item being hovered
    - `c`: The colour associated with the item being hovered
    - `return`: The html of the content inside the tooltip div
 - *nTickFormat*: `Bar.nTickFormat(yourFormattingFunction)`
    - `d`: The number from the tick
    - `return`: The value you want to display in its stead
 - *labelFormat*: `Bar.labelFormat(yourFormattingFunction)`
    - `d`: The value of the bar label you want to replace
    - `return`: The value you want to display in its stead

*Tip*: Unless you're doing a very custom format, you can use d3.format() with any of those options as well instead of yourFormattingFunction

```
(main.js)
---------------------
function yourFormattingFunction(d, c){
  console.log(d, c) // d is the data used to create the element being interacted with.
  
  let yourValue;
  
  //do whatever you want
  
  return yourValue;
}
```

Callbacks:
 - *Callback on click*: `Bar.callbackClick(yourCallback)`
 - *Callback on bar hover*: `Bar.callbackHover(yourCallback)`
 - *Callback on legend hover*: `Bar.callbackLegendHover(yourCallback)`;

```
(main.js)
---------------------
function yourCallback(d){
  console.log(d) // d is the data used to create the element being interacted with.
  
  //do whatever you want, no return value
}
```

Accessibility:
 - *Aria figure label*: `Bar.figureAriaLabel("Bargraph")`
 - *Aria figure description*: `Bar.figureAriaDescription('Your description. Default is generic how to use.')`

Create/customize the table:
 - *Create table in div*: `Bar.table(d3.select('div#wrapper1'))`
 - *Caption*: `Bar.tableCaption('Example caption')`
 - *Summary*: `Bar.tableSummary('Example - Text description')`
 - *Table placement*: `Bar.captionAbove(true);`
    - Places the caption above the data table functions (search, pagination, etc) instead of within


## OVERWRITING THE INIT :)
`CAUTION`: things may break

The init() and render() are seperate. This is because if you want to, you can overwrite many of the fundamental parts of the code.

Specifically, init() setups these things in this order:
 - *Container*: `initCategories()`
 - *initCategories*: `initCategories()`
 - *initData*: `initData()`
 - *initcScales*: `initcScales()`
 - *initNScale*: `initNScale()`
 - *initCSubScale*: `initCSubScale()`
 - *initColourScale*: `initColourScale()`
 - *initTextures*: `initTextures()`
 - *initAxes*: `initAxes()`
 - *initBarWidth*: `initBarWidth()`
 
With barcharts, I've most commonly had to overwritten the nScale. 

For example, I want to make it so that the barchart has values from 0 to 100 in it. So, I need to overwrite the domain of the nScale. This can be done in one line.

```
(main.js)
---------------------
bar
  
  // setup the barchart
  
  .init()
  .nScale(bar.nScale().domain([0, 100])) // get the nScale, overwrite the domain, set it as the nScale
  .render();
```"""
    elif graph_type == 'line':
        source = """/*
Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
*/

export class LineGraph {
    #data;
    #cKey; //becomes cSeries, remove
    #cSeries;
    #nKey;
    #categoryKey;

    #surKeys = [];

    #secondaryNDomain;

    #categoryLookup = {}
    #categoryReverseLookup = {}

    #cValues;
    #categories;
    #selectedCategories;

    #cScales = [];
    #cScale; //remove
    #nScale;
    #secondaryNScale;

    #axisGens;
    #lineGen;

    #container;
    #wrapper;
    #table;
    #tableCaption;
    #tableSummary = d3.select('html').attr('lang') == "fr" ? "Texte descriptif" : "Text description";
    #figureAriaLabel = "Chart";
    #figureAriaDescription = 'Chart description';

    #lineGroup;
    #pointGroup;
    #legendGroup;
    #axesGroup;
    #titleGroup;

    #gridlines = false;
    #displayPoints = false;
    #displayUncertainties = false;
    #interactive = false;
    #hoverFade = false;

    #upperUncertainty;
    #lowerUncertainty;
    #uncertaintyWidth = 8;

    #cAxisTickSkip = 0;
    #cAxisInitialHeight = 45;
    #cAxisDrop = 45;

    #width = 720;
    #height = 480;
    #margins = { l: 100, r: 60, t: 60, b: 100 };
    #defaultPadding = 0.25;
    #cPaddingSeries;

    #min;
    #max;

    // #colourSeries = ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#37A86F", "#edc949", "#af7aa1", "#ff9da7", "#9c755f", "#bab0ab"];
    #colourSeries = [
        "#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#37A86F",
        "#edc949", "#af7aa1", "#ff9da7", "#9c755f", "#bab0ab",
        "#6b9ac4", "#d84b2a", "#8c8c8c", "#69cc58", "#e279a3",
        "#665191", "#f7b6d2", "#dbdb8d", "#bcbd22", "#17becf",
        "#9467bd", "#69312d", "#e377c2", "#c49c94",
    ]
    #colourScale;
    #lineTypeSeries;
    #pointTypeSeries;
    #pointSymbolMap;
    #categorySymbolMap = {};
    #pointSize = 100;
    #pointSymbolDefault = d3.symbol().type(d3.symbolCircle).size(100);
    #defaultSymbol = 'circle';

    #graphTitle;
    #cAxisTitle;
    #nAxisTitle;
    #secondaryNTitle;

    #legendSpacing = [15, 22];
    #legendPosition = [550, 100];
    #legendOrientation = 'v';
    #legendLineLength = 50;
    #legendTextWrapWidth;

    #cAxisTitleSpacing = 50;
    #nAxisTitleSpacing = 60;
    #secondaryNTitleSpacing = 60;

    #transitionDuration = 1000;

    //functions/callbacks
    #tableHeaderFunction;
    #nTickFormat;

    // =============== CHAINING METHODS (get/set) ================= //
    data(inputData) {
        /*
        Parameters 
        ----------------
        inputData (type: array)
          - An array of object(s) with 2+ fields per object
          - Each object represents one row of data. Each field represents a column
        */
        if (arguments.length === 0) {
            return this.#data;
        }
        else {
            // Check input
            const nonEmptyArray = (typeof inputData == typeof []) &&
                (inputData.length > 0);
            let validElements = true;

            if (nonEmptyArray) {
                for (let v of inputData) {
                    if ((typeof v != typeof {}) ||
                        Object.keys(v).length <= 2) {

                        validElements = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && validElements) {
                this.#data = inputData;
                return this;
            }
            else {
                console.error('Data must be an array of object(s) with 2+ fields');
            }
        }
    }
    // cKey(inputKey) {
    //     /*
    //     Parameters 
    //     ----------------
    //     inputKey (type: string)
    //       - A string representing a key that the data field has. 
    //       - This string should indicate the key (data header) for the independent variable
    //     */
    //     if (arguments.length === 0) {
    //         return this.#cKey;
    //     }
    //     else {

    //         const validString = (typeof inputKey == typeof 'abc') && inputKey;

    //         if (validString) {
    //             this.#cKey = inputKey;
    //             return this;
    //         }
    //         else {
    //             console.error('cKey must be a non-empty string');
    //         }
    //     }
    // }
    cSeries(inputKeys) {
        /*
        Parameters 
        ----------------
        inputKeys (type: array)
          - An array of string(s) representing key(s) that the data field has. 
          - This array should indicate some key(s) to use for the numerical axis
        */

        if (arguments.length === 0) {
            return this.#cSeries;
        }
        else {
            // Check input
            const nonEmptyArray = (typeof inputKeys == typeof []) &&
                (inputKeys.length > 0);
            let validElements = true;

            if (nonEmptyArray) {
                for (let v of inputKeys) {
                    if ((typeof v != typeof 'abc') || !v) {
                        validElements = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && validElements) {
                this.#cSeries = inputKeys;
                return this;
            }
            else {
                console.error('cSeries must be an array of non-empty string(s)');
            }
        }
    }
    nKey(inputKey) {
        /*
        Parameters 
        ----------------
        inputKey (type: string)
          - A string representing a key that the data field has. 
          - This string should indicate the key (data header) for the dependent variable
        */
        if (arguments.length === 0) {
            return this.#nKey;
        }
        else {

            const validString = (typeof inputKey == typeof 'abc') && inputKey;

            if (validString) {
                this.#nKey = inputKey;
                return this;
            }
            else {
                console.error('nKey must be a non-empty string');
            }
        }
    }
    categoryKey(inputKey) {
        /*
        Parameters 
        ----------------
        inputKey (type: string)
          - A string representing a key that the data field has. 
          - This string should indicate the key (data header) for the dependent variable
        */
        if (arguments.length === 0) {
            return this.#categoryKey;
        }
        else {

            const validString = (typeof inputKey == typeof 'abc') && inputKey;

            if (validString) {
                this.#categoryKey = inputKey;
                return this;
            }
            else {
                console.error('categoryKey must be a non-empty string');
            }
        }
    }
    axisGens(input) {
        if (arguments.length === 0) {
            return this.#axisGens;
        }
        else {
            this.#axisGens = input;
            return this;
        }
    }
    secondaryNDomain(inputKey) {
        if (arguments.length === 0) {
            return this.#secondaryNDomain;
        }
        else {
            this.#secondaryNDomain = inputKey;
            return this;
        }
    }

    upperUncertainty(inputKey) {
        /*
        Parameters 
        ----------------
        inputKey (type: string)
          - A string representing a key that the data field has. 
          - This string should indicate the key (data header) for the dependent variable
        */
        if (arguments.length === 0) {
            return this.#upperUncertainty;
        }
        else {

            const validString = (typeof inputKey == typeof 'abc') && inputKey;

            if (validString) {
                this.#upperUncertainty = inputKey;
                return this;
            }
            else {
                console.error('upperUncertainty must be a non-empty string');
            }
        }
    }
    lowerUncertainty(inputKey) {
        /*
        Parameters 
        ----------------
        inputKey (type: string)
          - A string representing a key that the data field has. 
          - This string should indicate the key (data header) for the dependent variable
        */
        if (arguments.length === 0) {
            return this.#lowerUncertainty;
        }
        else {

            const validString = (typeof inputKey == typeof 'abc') && inputKey;

            if (validString) {
                this.#lowerUncertainty = inputKey;
                return this;
            }
            else {
                console.error('lowerUncertainty must be a non-empty string');
            }
        }
    }
    uncertaintyWidth(input) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing from the cAxis.
        */
        if (arguments.length === 0) {
            return this.#uncertaintyWidth;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input >= 0);

            if (validNum) {
                this.#uncertaintyWidth = input;
                return this;
            }
            else {
                console.error('uncertaintyWidth must be a number');
            }
        }
    }
    defaultPadding(inputPadding) {
        /*
        Parameters 
        ----------------
        inputPadding (type: number)
          - A number between 0 and 1 that represents a decimal percentage. 
          - This should indicate what percent of a bar's width should 
            be cut away for padding.
        */
        if (arguments.length === 0) {
            return this.#defaultPadding;
        }
        else {
            const validNum = (typeof inputPadding == typeof 5) &&
                (inputPadding <= 1) && (inputPadding >= 0);

            if (validNum) {
                this.#defaultPadding = inputPadding;
                return this;
            }
            else {
                console.error('defaultPadding must be a decimal number between 0-1');
            }
        }
    }
    graphTitle(inputTitle) {
        /*
        Parameters 
        ----------------
        inputTitle (type: string)
          - A string containing the title for the graph. 
        */

        if (arguments.length === 0) {
            return this.#graphTitle;
        }
        else {
            const validString = (typeof inputTitle == typeof 'abc') && inputTitle;

            if (validString) {
                this.#graphTitle = inputTitle;
                return this;
            }
            else {
                console.error('graphTitle must be a non-empty string');
            }
        }
    }
    cAxisTitle(inputTitle) {
        /*
        Parameters 
        ----------------
        inputTitle (type: string)
          - A string containing the title for the categorical axis. 
        */

        if (arguments.length === 0) {
            return this.#cAxisTitle;
        }
        else {
            const validString = (typeof inputTitle == typeof 'abc');

            if (validString) {
                this.#cAxisTitle = inputTitle;
                return this;
            }
            else {
                console.error('cAxisTitle must be a string');
            }
        }
    }
    nAxisTitle(inputTitle) {
        /*
        Parameters 
        ----------------
        inputTitle (type: string)
          - A string containing the title for the numerical axis. 
        */

        if (arguments.length === 0) {
            return this.#nAxisTitle;
        }
        else {
            const validString = (typeof inputTitle == typeof 'abc');

            if (validString) {
                this.#nAxisTitle = inputTitle;
                return this;
            }
            else {
                console.error('nAxisTitle must be a string');
            }
        }
    }
    secondaryNTitle(inputTitle) {
        /*
        Parameters 
        ----------------
        inputTitle (type: string)
          - A string containing the title for the numerical axis. 
        */

        if (arguments.length === 0) {
            return this.#secondaryNTitle;
        }
        else {
            const validString = (typeof inputTitle == typeof 'abc') && inputTitle;

            if (validString) {
                this.#secondaryNTitle = inputTitle;
                return this;
            }
            else {
                console.error('secondaryNTitle must be a non-empty string');
            }
        }
    }
    cAxisTitleSpacing(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing from the cAxis.
        */
        if (arguments.length === 0) {
            return this.#cAxisTitleSpacing;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5) &&
                (inputSpacing >= 0);

            if (validNum) {
                this.#cAxisTitleSpacing = inputSpacing;
                return this;
            }
            else {
                console.error('cAxisTitleSpacing must be a number');
            }
        }
    }
    nAxisTitleSpacing(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing from the cAxis.
        */
        if (arguments.length === 0) {
            return this.#nAxisTitleSpacing;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5) &&
                (inputSpacing >= 0);

            if (validNum) {
                this.#nAxisTitleSpacing = inputSpacing;
                return this;
            }
            else {
                console.error('nAxisTitleSpacing must be a number');
            }
        }
    }
    secondaryNTitleSpacing(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing from the cAxis.
        */
        if (arguments.length === 0) {
            return this.#secondaryNTitleSpacing;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5) &&
                (inputSpacing >= 0);

            if (validNum) {
                this.#secondaryNTitleSpacing = inputSpacing;
                return this;
            }
            else {
                console.error('secondaryNTitleSpacing must be a number');
            }
        }
    }
    cAxisTickSkip(input) {
        /*
        Parameters 
        ----------------
        input (type: number)
          - A number for the number of ticks skipped after the first. Display, skip n, display, skip n, etc.
        */
        if (arguments.length === 0) {
            return this.#cAxisTickSkip;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input >= 0);

            if (validNum) {
                this.#cAxisTickSkip = input;
                return this;
            }
            else {
                console.error('cAxisTickSkip must be a number');
            }
        }
    }
    cAxisInitialHeight(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing between the graph and the legend.
        */
        if (arguments.length === 0) {
            return this.#cAxisInitialHeight;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5);

            if (validNum) {
                this.#cAxisInitialHeight = inputSpacing;
                return this;
            }
            else {
                console.error('cAxisInitialHeight must be a number');
            }
        }
    }
    cAxisDrop(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing between the graph and the legend.
        */
        if (arguments.length === 0) {
            return this.#cAxisDrop;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5);

            if (validNum) {
                this.#cAxisDrop = inputSpacing;
                return this;
            }
            else {
                console.error('cAxisDrop must be a number');
            }
        }
    }
    transitionDuration(input) {
        if (arguments.length === 0) {
            return this.#transitionDuration;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input >= 0);

            if (validNum) {
                this.#transitionDuration = input;
                return this;
            }
            else {
                console.error('transitionDuration must be a non-negative number');
            }
        }
    }
    width(inputWidth) {
        /*
        Parameters 
        ----------------
        inputWidth (type: number)
          - A non-negative number for the width of the bar graph.
        */
        if (arguments.length === 0) {
            return this.#width;
        }
        else {
            const validNum = (typeof inputWidth == typeof 5) &&
                (inputWidth >= 0);

            if (validNum) {
                this.#width = inputWidth;
                return this;
            }
            else {
                console.error('width must be a non-negative number');
            }
        }
    }
    height(inputHeight) {
        /*
        Parameters 
        ----------------
        inputHeight (type: number)
          - A non-negative number for the height of the bar graph. 
        */

        if (arguments.length === 0) {
            return this.#height;
        }
        else {
            const validNum = (typeof inputHeight == typeof 5) &&
                (inputHeight >= 0);

            if (validNum) {
                this.#height = inputHeight;
                return this;
            }
            else {
                console.error('height must be a non-negative number');
            }
        }
    }
    margins(inputMargins) {
        /*
        Parameters 
        ----------------
        inputMargins (type: array)
          - An array of numbers representing margins between the 
            bar graph and the SVG container. 
          - Specify margins in clockwise order (top, right, bottom, left)
        */
        if (arguments.length === 0) {
            return this.#margins;
        }
        else {
            // Validate nums
            let validNums = true;
            for (let n of inputMargins) {
                if (typeof n != typeof 5) {
                    validNums = false;
                    break;
                }
            }

            // Set fields
            if (validNums) {
                this.#margins = {
                    l: inputMargins[3],
                    r: inputMargins[1],
                    t: inputMargins[0],
                    b: inputMargins[2]
                };
                return this;
            }
            else {
                console.error(
                    'Please input an array of four numbers to configure top,' +
                    'right, bottom, and left margins in that order.'
                );
            }
        }
    }
    container(inputContainer) {
        /*
        Parameters 
        ----------------
        inputContainer (type: D3.js selection)
          - A SVG DOM element to render the bar graph in 
            (inputted as a d3.js selection)
        */
        if (arguments.length === 0) {
            return this.#container;
        }
        else {
            this.#container = inputContainer;
            return this;
        }
    }
    wrapper(inputWrapper) {
        /*
        Parameters 
        ----------------
        inputWrapper (type: D3.js selection)
          - A div containing the container element to render the 
            tooltips in (inputted as a d3.js selection)
        */
        if (arguments.length === 0) {
            return this.#wrapper;
        }
        else {
            this.#wrapper = inputWrapper;
            return this;
        }
    }
    lineGroup(input) {
        if (arguments.length === 0) {
            return this.#lineGroup;
        }
        else {
            this.#lineGroup = input;
            return this;
        }
    }
    pointGroup(input) {
        if (arguments.length === 0) {
            return this.#pointGroup;
        }
        else {
            this.#pointGroup = input;
            return this;
        }
    }
    legendGroup(input) {
        if (arguments.length === 0) {
            return this.#legendGroup;
        }
        else {
            this.#legendGroup = input;
            return this;
        }
    }
    axesGroup(input) {
        if (arguments.length === 0) {
            return this.#axesGroup;
        }
        else {
            this.#axesGroup = input;
            return this;
        }
    }
    titleGroup(input) {
        if (arguments.length === 0) {
            return this.#titleGroup;
        }
        else {
            this.#titleGroup = input;
            return this;
        }
    }
    table(inputTable) {
        /*
        Parameters 
        ----------------
        inputWrapper (type: D3.js selection)
          - A div to append the table to.
        */
        if (arguments.length === 0) {
            return this.#table;
        }
        else {
            this.#table = inputTable;
            return this;
        }
    }
    tableCaption(inputCaption) {
        /*
        Parameters 
        ----------------
        inputCaption (type: string)
          - A string containing the caption for the table. 
        */

        if (arguments.length === 0) {
            return this.#tableCaption;
        }
        else {
            const validString = (typeof inputCaption == typeof 'abc') && inputCaption;

            if (validString) {
                this.#tableCaption = inputCaption;
                return this;
            }
            else {
                console.error('tableCaption must be a non-empty string');
            }
        }
    }
    tableSummary(inputSummary) {
        /*
        Parameters 
        ----------------
        inputCaption (type: string)
          - A string containing the caption for the table. 
        */

        if (arguments.length === 0) {
            return this.#tableSummary;
        }
        else {
            const validString = (typeof inputSummary == typeof 'abc') && inputSummary;

            if (validString) {
                this.#tableSummary = inputSummary;
                return this;
            }
            else {
                console.error('tableSummary must be a non-empty string');
            }
        }
    }
    figureAriaLabel(input) {
        if (arguments.length === 0) {
            return this.#figureAriaLabel;
        }
        else {
            const validString = (typeof input == typeof 'abc') && input;

            if (validString) {
                this.#figureAriaLabel = input
                return this;
            }
            else {
                console.error('figureAriaLabel must be a non-empty string');
            }
        }
    }
    figureAriaDescription(input) {
        if (arguments.length === 0) {
            return this.#figureAriaDescription;
        }
        else {
            const validString = (typeof input == typeof 'abc') && input;

            if (validString) {
                this.#figureAriaDescription = input
                return this;
            }
            else {
                console.error('figureAriaDescription must be a non-empty string');
            }
        }
    }
    // cScale(inputCScale) {
    //     /*
    //     Parameters 
    //     ----------------
    //     inputCScale (type: function)
    //       - A d3.scale function that will be used to space the labels and 
    //         categorical position of bars.
    //     */
    //     if (arguments.length === 0) {
    //         return this.#cScale;
    //     }
    //     else {
    //         this.#cScale = inputCScale;
    //         return this;
    //     }
    // }
    cScales(inputCScale) {
        /*
        Parameters 
        ----------------
        inputCScale (type: function)
          - A d3.scale function that will be used to space the labels and 
            categorical position of bars.
        */
        if (arguments.length === 0) {
            return this.#cScales;
        }
        else {
            this.#cScales = inputCScale;
            return this;
        }
    }
    nScale(inputNScale) {
        /*
        Parameters 
        ----------------
        inputNScale (type: function)
          - A d3.scale function that will be used to set the height of the bars
        */
        if (arguments.length === 0) {
            return this.#nScale;
        }
        else {
            this.#nScale = inputNScale;
            return this;
        }
    }
    colourSeries(inputKeys) {
        /*
        Parameters 
        ----------------
        inputKeys (type: array)
          - An array of string(s) representing key(s) that the data field has currently selected. 
          - This array should indicate some key(s) to use for the numerical axis
        */

        if (arguments.length === 0) {
            return this.#colourSeries;
        }
        else {
            // Check input
            const nonEmptyArray = (typeof inputKeys == typeof []) &&
                (inputKeys.length > 0);
            let validElements = true;

            if (nonEmptyArray) {
                for (let v of inputKeys) {
                    if ((typeof v != typeof 'abc') || !v) {
                        validElements = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && validElements) {
                this.#colourSeries = inputKeys;
                return this;
            }
            else {
                console.error('colourSeries must be an array of non-empty string(s)');
            }
        }
    }
    lineTypeSeries(inputKeys) {
        /*
        Parameters 
        ----------------
        inputKeys (type: array)
          - An array of string(s) representing key(s) that denote which lines are dashed, dotted, straight
        */

        let accepted = ["dashed", "dotted", "solid"]

        if (arguments.length === 0) {
            return this.#lineTypeSeries;
        }
        else {
            // Check input
            const nonEmptyArray = (typeof inputKeys == typeof []) &&
                (inputKeys.length > 0);
            let validElements = true;

            if (nonEmptyArray) {
                for (let v of inputKeys) {
                    if ((typeof v != typeof 'abc') || !v || !accepted.includes(v)) {
                        validElements = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && validElements) {
                this.#lineTypeSeries = inputKeys;
                return this;
            }
            else {
                console.error('lineTypeSeries must be an array of non-empty string(s) where the options are "dashed", "dotted", and "solid"');
            }
        }
    }
    pointTypeSeries(inputKeys) {
        /*
        Parameters 
        ----------------
        inputKeys (type: array)
          - An array of string(s) representing key(s) that denote which lines are dashed, dotted, straight
        */

        let accepted = ["circle", "square", "diamond", "triangle"]

        if (arguments.length === 0) {
            return this.#pointTypeSeries;
        }
        else {
            // Check input
            const nonEmptyArray = (typeof inputKeys == typeof []) &&
                (inputKeys.length > 0);
            let validElements = true;

            if (nonEmptyArray) {
                for (let v of inputKeys) {
                    if ((typeof v != typeof 'abc') || !v || !accepted.includes(v)) {
                        validElements = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && validElements) {
                this.#pointTypeSeries = inputKeys;
                return this;
            }
            else {
                console.error('pointTypeSeries must be an array of non-empty string(s) where the options are "circle", "square", "diamond", and "triangle"');
            }
        }
    }
    pointSize(inputSize) {
        /*
        Parameters 
        ----------------
        inputWidth (type: number)
          - A non-negative number for the pointSize of the bar graph.
        */
        if (arguments.length === 0) {
            return this.#pointSize;
        }
        else {
            const validNum = (typeof inputSize == typeof 5) &&
                (inputSize >= 0);

            if (validNum) {
                this.#pointSize = inputSize;
                return this;
            }
            else {
                console.error('pointSize must be a non-negative number');
            }
        }
    }
    colourScale(inputColourScale) {
        /*
        Parameters 
        ----------------
        inputCSubScale (type: function)
          - A d3.scaleOrdinal function that will be used to colour the bars.
        */
        if (arguments.length === 0) {
            return this.#colourScale;
        }
        else {
            this.#colourScale = inputColourScale;
            return this;
        }
    }
    legendSpacing(input) {
        if (arguments.length === 0) {
            return this.#legendSpacing;
        }
        else {
            const nonEmptyArray = (typeof input == typeof []) &&
                (input.length == 2);
            let allInts = true;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && allInts) {
                this.#legendSpacing = input
                return this;
            }
            else {
                console.error('legendSpacing must be an array of 2 numbers, where the first reprents the horizontal space between the symbol and the text, and the second the vertical/horizontal space between subgroups.');
            }
        }
    }
    legendPosition(input) {
        if (arguments.length === 0) {
            return this.#legendPosition;
        }
        else {
            const nonEmptyArray = (typeof input == typeof []) &&
                (input.length == 2);
            let allInts = true;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && allInts) {
                this.#legendPosition = input
                return this;
            }
            else {
                console.error('legendPosition must be an array of 2 numbers, where the numbers represent the x and y translation of the legend group');
            }
        }
    }
    legendOrientation(input) {
        /*
        Parameters 
        ----------------
        input (type: char)
          - A number for the spacing between the graph and the legend.
        */
        let accepted = ["h", "v"]

        if (arguments.length === 0) {
            return this.#legendOrientation;
        }
        else {
            const valid = (typeof input == typeof 'a' && accepted.includes(input));

            if (valid) {
                this.#legendOrientation = input;
                return this;
            }
            else {
                console.error('legendOrientation must be "v" for vertical, or "h" for horizontal');
            }
        }
    }
    legendLineLength(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing from the cAxis.
        */
        if (arguments.length === 0) {
            return this.#legendLineLength;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5) &&
                (inputSpacing >= 0);

            if (validNum) {
                this.#legendLineLength = inputSpacing;
                return this;
            }
            else {
                console.error('legendLineLength must be a number');
            }
        }
    }
    legendTextWrapWidth(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing from the cAxis.
        */
        if (arguments.length === 0) {
            return this.#legendTextWrapWidth;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5) &&
                (inputSpacing >= 0);

            if (validNum) {
                this.#legendTextWrapWidth = inputSpacing;
                return this;
            }
            else {
                console.error('legendTextWrapWidth must be a number');
            }
        }
    }
    cPaddingSeries(input) {
        if (arguments.length === 0) {
            return this.#cPaddingSeries;
        }
        else {
            this.#cPaddingSeries = input;
            return this;
        }
    }

    gridlines(inputToggle) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph have gridlines. False otherwise.
        */

        if (arguments.length === 0) {
            return this.#gridlines;
        }
        else {
            const validBool = (typeof inputToggle == typeof true);

            if (validBool) {
                this.#gridlines = inputToggle;
                return this;
            }
            else {
                console.error('gridlines must be a boolean');
            }
        }
    }
    displayPoints(inputToggle) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph have gridlines. False otherwise.
        */

        if (arguments.length === 0) {
            return this.#displayPoints;
        }
        else {
            const validBool = (typeof inputToggle == typeof true);

            if (validBool) {
                this.#displayPoints = inputToggle;
                return this;
            }
            else {
                console.error('displayPoints must be a boolean');
            }
        }
    }
    displayUncertainties(inputToggle) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph have gridlines. False otherwise.
        */

        if (arguments.length === 0) {
            return this.#displayUncertainties;
        }
        else {
            const validBool = (typeof inputToggle == typeof true);

            if (validBool) {
                this.#displayUncertainties = inputToggle;
                if ((!this.#upperUncertainty || !this.#lowerUncertainty) && inputToggle) {
                    console.warn("lowerUncertainty and upperuncertainty keys must both be set for them to display")
                }
                return this;
            }
            else {
                console.error('displayUncertainties must be a boolean');
            }
        }
    }
    interactive(inputToggle) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph interactive. False otherwise.
        */
        if (arguments.length === 0) {
            return this.#interactive;
        }
        else {
            const validBool = (typeof inputToggle == typeof true);

            if (validBool) {
                this.#interactive = inputToggle;
                return this;
            }
            else {
                console.error('interactive must be a boolean');
            }
        }
    }
    hoverFade(inputToggle) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph interactive. False otherwise.
        */
        if (arguments.length === 0) {
            return this.#hoverFade;
        }
        else {
            const validBool = (typeof inputToggle == typeof true);

            if (validBool) {
                this.#hoverFade = inputToggle;
                return this;
            }
            else {
                console.error('hoverFade must be a boolean');
            }
        }
    }

    tableHeaderFunction(input) {
        if (arguments.length === 0) {
            return this.#tableHeaderFunction;
        }
        else {
            this.#tableHeaderFunction = input
            return this;
        }
    }
    nTickFormat(input) {
        if (arguments.length === 0) {
            return this.#nTickFormat;
        }
        else {
            this.#nTickFormat = input
            return this;
        }
    }

    // ============== PUBLIC (setup) ============== //
    initContainer() {
        /*
        Assigns the basic attributes to the container svg.
        
        Parameters
        ----------------
        undefined
        - Note: Requires height and width to have a value

        Returns
        ----------------
        undefined
        
        */

        this.#container
            // .attr('height', this.#height)
            .attr('width', '100%')
            .attr('viewBox', `0 0 ${this.#width} ${this.#height}`)
            .attr("perserveAspectRatio", "xMinyMin meet")
            .attr('aria-label', this.#figureAriaLabel)
            .attr('aria-description', this.#figureAriaDescription)
            .attr('tabindex', 0)
    }
    initCategories() {
        let categories = [];
        this.#data.map(el => {
            let cat = el[this.#categoryKey];
            if (!categories.includes(cat)) {
                categories.push(cat)
            }
        })
        this.#categoryLookup = {};
        this.#categoryReverseLookup = {};

        categories.map((el, i) => {
            this.#categoryLookup[el] = "val" + i;
            this.#categoryReverseLookup["val" + i] = el;
        })
        // console.log('categories', categories)
        this.#categories = categories;
    }
    initSymbols() {
        this.#pointSymbolDefault.size(this.#pointSize)

        let triangle = d3.symbol().type(d3.symbolTriangle).size(this.#pointSize);
        let circle = d3.symbol().type(d3.symbolCircle).size(this.#pointSize);
        let square = d3.symbol().type(d3.symbolSquare).size(this.#pointSize);
        let diamond = d3.symbol().type(d3.symbolDiamond2).size(this.#pointSize);

        this.#pointSymbolMap = {
            "circle": circle,
            "square": square,
            "diamond": diamond,
            "triangle": triangle
        }
        if (this.#pointTypeSeries) {
            this.#categories.map((cat, i) => {
                this.#categorySymbolMap[cat] = this.#pointTypeSeries[i];
            })
        }
    }
    initNScale(update = true) {
        /*
          This function initialises a linear scale to place line heights.
        
          Parameters 
          -----------------
          log (type: bool)
            - Whether to set the bar height with a log scale.
        */
        // console.log('nKey', this.#nKey)
        // console.log('data', this.#data)
        this.#selectedCategories = this.#findSelectedCategories();
        // console.log('sCat', this.#selectedCategories)
        let data = this.#data;
        if (!update && this.#selectedCategories && this.#selectedCategories.length != 0) {
            // console.log()
            data = data.filter(d => {
                // console.log(d[this.#categoryKey])
                return this.#selectedCategories.includes(d[this.#categoryKey])
            })
        }
        // console.log('filteredData', data)
        this.#min = d3.min(data, (d) => {
            // console.log('posMin', parseFloat(d[this.#nKey]))

            // if (this.#selectedCategories && this.#selectedCategories.includes(d[this.#categoryKey])){
            //     console.log(d[this.#categoryKey], d[this.#nKey])
            //     return parseFloat(d[this.#nKey])
            // }
            // else if (!this.#selectedCategories)
            //     return parseFloat(d[this.#nKey])
            return parseFloat(d[this.#nKey])
        });
        this.#max = d3.max(data, (d) => {
            // if (this.#selectedCategories && this.#selectedCategories.includes(d[this.#categoryKey])){
            //     return parseFloat(d[this.#nKey])
            // }
            // else if (!this.#selectedCategories)
            //     return parseFloat(d[this.#nKey])
            return parseFloat(d[this.#nKey])
        });

        // console.log("min", this.#min)
        // console.log("max", this.#max)

        this.#nScale = d3
            .scaleLinear()
            .domain([this.#min, this.#max])
            .range([(this.#height - this.#margins.b), this.#margins.t]);

    }
    initCScales() {
        /* 
        Initialises a bandscale for the categorical axis
        
        Parameters
        -------------------
        undefined
        - Though note that this method relies on values of #data, #cSeries, 
          #margins, #padding, and #width. Please initialise those before calling the method
          
        Returns
        -------------------
        undefined
        */

        this.#surKeys = []
        this.#cScales = []

        let cSeriesLength = this.#cSeries.length;

        if (cSeriesLength == 1) {
            // let myDomain = d3.extent(this.#data, (d) => { return d[this.#cKey]; }) // get range of values along c axis
            let myDomain = [...new Set(this.#data.map(d => d[this.#cSeries[0]]))]; // get unique cValues
            this.#cValues = myDomain;
            // console.log('domain', myDomain)

            let scale = d3
                // .scaleLinear()
                .scalePoint()
                .domain(myDomain) //this.#data.map(d => d[this.#cSeries])
                .range([this.#margins.l, this.#width - this.#margins.r])

            this.#cScales.push(scale)
        }
        else {
            this.#cSeries.map((group, i) => {
                let scale;
                if (i == cSeriesLength - 1) {
                    //line scale needed
                    let myDomain = [...new Set(this.#data.map(d => d[this.#cSeries[cSeriesLength - 1]]))]; // get unique cValues
                    this.#surKeys.push(myDomain)

                    scale = d3
                        // .scaleLinear()
                        .scalePoint()
                        .domain(myDomain) //this.#data.map(d => d[this.#cSeries])
                        .range([0, this.#cScales[i - 1].bandwidth()])
                }
                else {
                    //scale band
                    //get unique keys from group
                    let keys = []
                    this.#data.map(el => {
                        if (!keys.includes(el[group])) {
                            keys.push(el[group])
                        }
                    })
                    this.#surKeys.push(keys)

                    //create cScales
                    if (i == 0) {
                        scale = d3
                            .scaleBand()
                            .domain(this.#surKeys[i])
                            .range([this.#margins.l, this.#width - this.#margins.r])
                            .padding([this.#cPaddingSeries ? this.#cPaddingSeries[i] : this.#defaultPadding]);
                    }
                    else {
                        scale = d3
                            .scaleBand()
                            .domain(this.#surKeys[i])
                            .range([0, this.#cScales[i - 1].bandwidth()])
                            .padding([this.#cPaddingSeries ? this.#cPaddingSeries[i] : this.#defaultPadding])
                    }
                }
                this.#cScales.push(scale);
            })
        }


        // console.log("surKeys", this.#surKeys)
        // console.log("scales", this.#cScales)

    }
    initSecondaryScale() {
        this.#secondaryNScale = d3
            .scaleLinear()
            .domain(this.#secondaryNDomain)
            .range([(this.#height - this.#margins.b), this.#margins.t]);
    }
    initColourScale() {
        /*
        Initializes a scaleOrdinal for the colours of the bars.
        */
        this.#colourScale = d3
            .scaleOrdinal()
            .domain(this.#categories)
            .range(this.#colourSeries)
    }
    initAxes(cAxisOptions = {}, nAxisOptions = {}, sAxisOptions = {}) {
        /*
        This function initialises the bottom and left scales for the bar graph
        
        Parameters
        -----------------
        cAxisOptions/nAxisOptions (type: object)
        - Objects with settings to configure the categorical and numerical axes. 
        - Input settings as key-value pairs in the objects. 
        - Valid keys are `ticks`, `tickValues`, `tickFormat`, `tickPadding`, and
          `tickSize`.
        - See d3.js documentation for valid values;
        - Also note that this function relies on #cScale and #nScale. 
          Make sure these are initialised.
          
        Returns
        -----------------
        undefined
        */

        // Create axes
        let n = d3.axisLeft(this.#nScale);
        let c = [];
        this.#cScales.map(scale => {
            c.push(d3.axisBottom(scale));
        })
        let s;


        // Set options
        function setOptions(ax, obj) {
            if (obj.ticks) ax.ticks(obj.ticks);
            if (obj.tickValues) ax.tickValues(obj.tickValues);
            if (obj.tickFormat) ax.tickFormat(obj.tickFormat);
            if (obj.tickPadding) ax.tickPadding(obj.tickPadding);
            if (obj.tickSizeOuter) ax.tickSizeOuter(obj.tickSizeOuter);
            if (obj.tickSizeInner) ax.tickSizeInner(obj.tickSizeInner);
        }

        // console.log(cAxisOptions.ticks)

        if (this.#secondaryNDomain) {
            s = d3.axisRight(this.#secondaryNScale);
            setOptions(s, sAxisOptions);
        }

        setOptions(n, nAxisOptions);
        setOptions(c, cAxisOptions);


        // console.log(c)

        this.#axisGens = { c, n, s };
    }
    init() {
        this.initContainer();
        this.initCategories();
        this.initSymbols();
        this.initNScale();
        this.initCScales();
        if (this.#secondaryNDomain) {
            this.initSecondaryScale();
        }
        this.initColourScale();

        let nAxisOptions = {};
        let cAxisOptions = {};
        let sAxisOptions = {};
        if (this.#gridlines) {
            const gridHeight = this.#height - this.#margins.b - this.#margins.t;
            const gridWidth = this.#width - this.#margins.l - this.#margins.r;
            const gridlineLength = -gridWidth

            nAxisOptions["tickSizeInner"] = gridlineLength
            nAxisOptions["tickPadding"] = 10
        }
        if (this.#cAxisTickSkip > 0) {
            cAxisOptions['tickValues'] = this.#cScale.domain().filter((d, i) => i % this.#cAxisTickSkip === 0)
        }
        if (this.#nTickFormat){
          nAxisOptions["tickFormat"] = this.#nTickFormat;
        }

        this.initAxes(cAxisOptions, nAxisOptions, sAxisOptions);
        return this;
    }
    render() {
        this.#renderAxes();
        this.#renderLines();
        this.#renderTitles();
        this.#renderLegend();

        if (this.#hoverFade) {
            this.#addHoverFadeout();
        }

        if (this.#interactive) {
            this.#addInteraction();
        }

        this.#setTabbing();

        if (this.#table) {
            this.#addTable();
        }

        return this;
    }
    update() {
        this.#updateAxes();
        this.#renderLines();
        this.#renderTitles();
        this.#renderLegend();

        if (this.#hoverFade) {
            this.#addHoverFadeout();
        }

        if (this.#interactive) {
            this.#addInteraction();
        }

        if (this.#table) {
            this.#addTable();
        }

        return this;
    }

    // ============== PRIVATE (logic) ============== //
    #renderFancyAxes(axesGroup, orientation) {
        let that = this;
        const height = this.#height - this.#margins.b

        let axisInitialHeight = this.#cAxisInitialHeight;
        // let axisInitialHeight = 90;
        let axisDrop = this.#cAxisDrop;
        // let axisDrop = 45;
        let hAxis;

        function addAxis(selection, axisGen, i, yPos, xPos, series = null, displayPath = true) {
            if (series == null) {
                // console.log("nullPosition", xPos, height)
                hAxis = selection
                    .append('g')
                    .attr('class', orientation + i)
                    .attr('transform', `translate(${xPos}, ${height})`)
                    // .attr('transform', `translate(${height}, ${0})`)
                    .call(axisGen)
            }
            else {
                // console.log(selection)
                hAxis = selection.selectAll('g')
                    .data(series)
                    .append('g')
                    .attr('transform', `translate(${-that.#cScales[i-1].bandwidth()/2}, ${0})`)
                    .attr('class', orientation + i)
                    .call(axisGen)
                // console.log(hAxis)
            }

            let wrapWidth = that.#cScales[i].bandwidth() + that.#cScales[i].padding(); //that.#cAxisTitleSpacing

            hAxis
                .selectAll('.tick text')
                .attr('transform', `translate(0, ${yPos})`)
            // .call(that.#wrap, wrapWidth)
            // .call(that.#fitToConstraints, that.#vertical ? that.#cAxisTitleSpacing : that.#cScales[i].bandwidth() + that.#cScales[i].padding(), that) //that.#cAxisTitleSpacing
            // .call(that.#fitToConstraints, that.#cAxisTitleSpacing, that) //that.#cAxisTitleSpacing


            hAxis
                .selectAll('.tick line')
                .attr('y1', 0)
                .attr('y2', 0)
                .attr('x1', 0)
                .attr('x2', 0)

            if (!displayPath) {
                hAxis.select("path").remove()
            }
        }

        // console.log(this.#axisGens);
        this.#axisGens[orientation].map((cAxisGen, i) => {
            let yPos = axisInitialHeight - axisDrop * i;
            let xPos = 0;
            if (i == 0) {
                addAxis(axesGroup, cAxisGen, i, yPos, xPos)
            }
            else {
                // console.log(this.#surKeys[i-1])
                addAxis(hAxis, cAxisGen, i, yPos, xPos, this.#surKeys[i - 1], false)
            }
        })
    }
    #renderAxes() {
        // // Create subgroup
        // const axes = this.#container
        //     .append('g')
        //     .attr('class', 'axes');

        // // Render vertical axis
        // const v = 'n';
        // let vAxis = axes
        //     .append('g')
        //     .attr('class', v)
        //     .attr('transform', `translate(${this.#margins.l},0)`)
        //     .call(this.#axisGens[v]);

        // //render secondary vertical axis
        // if (this.#secondaryNDomain) {
        //     const s = 's';
        //     let sAxis = axes.append('g')
        //         .attr('class', s)
        //         .attr('transform', `translate(${this.#width - this.#margins.r},0)`)
        //         .call(this.#axisGens[s]);
        // }


        // // Render horizontal axis
        // const h = 'c';
        // const height = this.#height - this.#margins.b;

        // let hAxis = axes
        //     .append('g')
        //     .attr('class', h)
        //     .attr('transform', `translate(0, ${height})`)
        //     .call(this.#axisGens[h])

        // if (h == 'c') {
        //     hAxis
        //         .selectAll('.tick text')
        //     // .call(this.#wrap, this.#cScale.bandwidth() + this.#cScale.padding())
        //     // .call(this.#fitToConstraints, this.#cAxisTitleSpacing, this)
        // }
        // Create subgroup
        const axes = this.#container
            .append('g')
            .attr('class', 'axes');

        this.#axesGroup = axes;

        // Render vertical axis
        const v = 'n';
        let vAxis = axes
            .append('g')
            .attr('class', v)
            .attr('transform', `translate(${this.#margins.l},0)`)
            .call(this.#axisGens[v]);

        // Render horizontal axis
        const h = 'c';
        this.#renderFancyAxes(axes, h)

    }
    // #updateAxes() {
    //     const that = this;
    //     const axes = this.#container.select(".axes")

    //     // update vertical axis
    //     const v = 'n';

    //     let vText = []
    //     axes
    //         .select(`.${v}`)
    //         .selectAll('.tick text')
    //         .each(el => vText.push(el))

    //     // console.log(hText, this.#cScale.domain())

    //     axes
    //         .select(`.${v}`)
    //         .transition().duration(this.#transitionDuration)
    //         .call(this.#axisGens[v]);


    //     // update horizontal axis
    //     const h = 'c';

    //     const height = this.#height - this.#margins.b

    //     let hText = []
    //     axes
    //         .select(`.${h}`)
    //         .selectAll('.tick text')
    //         .each(el => hText.push(el))

    //     // console.log(hText, this.#cScale.domain())

    //     if (hText.join("") != this.#cScale.domain().join("")) {
    //         let hAxis = axes
    //             .select(`.${h}`)
    //             .call(this.#axisGens[h])
    //         hAxis
    //             .selectAll(".tick text")
    //         // .call(this.#wrap, this.#cScale.bandwidth() + this.#cScale.padding())
    //         // .call(this.#fitToConstraints, this.#cAxisTitleSpacing, this)

    //         hAxis
    //             .selectAll(".tick text")
    //             .style("opacity", 0)
    //             .transition().duration(this.#transitionDuration)
    //             .style("opacity", 1)
    //     }
    //     else {
    //         axes
    //             .select(`.${h}`)
    //             .transition().duration(this.#transitionDuration)
    //             .call(this.#axisGens[h]);
    //     }
    // }
    #updateAxes() {
        const that = this;
        const axes = this.#axesGroup;

        // update vertical axis
        const v = 'n';

        let vText = []
        axes
            .select(`.${v}`)
            .selectAll('.tick text')
            .each(el => vText.push(el))

        // console.log(hText, this.#cScale.domain())
        if (v == 'n') {
            axes
                .select(`.${v}`)
                .transition().duration(this.#transitionDuration)
                .call(this.#axisGens[v]);
        }
        else {
            let joinAxisText = () => {
                let arrayOfJoins = [];
                this.#cSeries.map((c, i) => {
                    //get text for each cSeries row before being replaced to use for transition comparing down the line
                    let cText = []
                    axes
                        .selectAll(`.${v + i} > .tick > text`)
                        .each(el => cText.push(el))
                    //ensure the text array is unique to match the domain format
                    // myArray.push([... new Set(cText)].join(""))
                    arrayOfJoins.push(cText.join(""))
                })
                return arrayOfJoins;
            }
            //get hAxis text
            let vText = joinAxisText();

            //remove axes
            axes.select(`.${v}0`).remove();
            //render axes again
            this.#renderFancyAxes(axes, v)
            //get newly rendered hAxis text
            let newVText = joinAxisText();
            //find which need to be transitioned in by comparing past axis text to new axis text
            this.#cSeries.map((c, i) => {
                if (newVText[i] != vText[i])
                    axes.selectAll(`.${v + i} > .tick > text`)
                    .attr('opacity', 0)
                    .transition().duration(this.#transitionDuration)
                    .attr("opacity", 1)
            })
        }

        // update horizontal axis
        const h = 'c';

        const height =
            this.#height - this.#margins.b;

        if (h == 'n') {
            axes
                .select(`.${h}`)
                .transition().duration(this.#transitionDuration)
                .call(this.#axisGens[h]);
        }
        else {
            let joinAxisText = () => {
                let arrayOfJoins = [];
                this.#cSeries.map((c, i) => {
                    //get text for each cSeries row before being replaced to use for transition comparing down the line
                    let cText = []
                    axes
                        .selectAll(`.${h + i} > .tick > text`)
                        .each(el => cText.push(el))
                    //ensure the text array is unique to match the domain format
                    // myArray.push([... new Set(cText)].join(""))
                    arrayOfJoins.push(cText.join(""))
                })
                return arrayOfJoins;
            }
            //get hAxis text
            let hText = joinAxisText();

            //remove axes
            axes.select(`.${h}0`).remove();
            //render axes again
            this.#renderFancyAxes(axes, h)
            //get newly rendered hAxis text
            let newHText = joinAxisText();
            //find which need to be transitioned in by comparing past axis text to new axis text
            this.#cSeries.map((c, i) => {
                if (newHText[i] != hText[i])
                    axes.selectAll(`.${h + i} > .tick > text`)
                    .attr('opacity', 0)
                    .transition().duration(this.#transitionDuration)
                    .attr("opacity", 1)
            })
        }
    }
    #pathTween(lineGen, precision) {
        return function(d, k) {
            let d1 = lineGen(d)
            const path0 = this;
            const path1 = path0.cloneNode();
            path1.setAttribute("d", d1);
            const n0 = path0.getTotalLength();
            const n1 = path1.getTotalLength();

            // Uniform sampling of distance based on specified precision.
            const distances = [0];
            const dt = precision / Math.max(n0, n1);
            let i = 0;
            while ((i += dt) < 1) distances.push(i);
            distances.push(1);

            // Compute point-interpolators at each distance.
            const points = distances.map((t) => {
                const p0 = path0.getPointAtLength(t * n0);
                const p1 = path1.getPointAtLength(t * n1);
                return d3.interpolate([p0.x, p0.y], [p1.x, p1.y]);
            });

            return (t) => t < 1 ? "M" + points.map((p) => p(t)).join("L") : d1;
        };
    }
    #updateUncertaintyLine(selection, key, vertical = true) {
        selection
            .transition()
            .duration(this.#transitionDuration)
            .attr('y1', d => vertical ? this.#nScale(d[this.#lowerUncertainty]) : this.#nScale(d[key]))
            .attr('y2', d => vertical ? this.#nScale(d[this.#upperUncertainty]) : this.#nScale(d[key]))
            .attr('x1', d => {
                return vertical ? this.#cScale(d[this.#cKey]) : this.#cScale(d[this.#cKey]) - this.#uncertaintyWidth / 2
            })
            .attr('x2', d => vertical ? this.#cScale(d[this.#cKey]) : this.#cScale(d[this.#cKey]) + this.#uncertaintyWidth / 2)
    }
    #calcLineXPos(d) {
        // console.log(d)
        let xPos = 0;

        this.#cSeries.map((c, i) => {
            if (i != this.#cSeries.length - 1) {
                xPos += this.#cScales[i](d[c])
            }

            // console.log(this.#cScales)
            // console.log(d.data[c])
        })
        // console.log(xPos)
        return xPos;
    }
    #renderLines() {
        // this.#container
        if (!this.#lineGroup)
            this.#lineGroup = this.#container.append('g').attr('class', 'lines')

        // console.log('cScales', this.#cScales)
        this.#lineGen = d3.line()
            .x((d) => { return this.#cScales[this.#cScales.length - 1](d[this.#cSeries[this.#cSeries.length - 1]]); })
            .y((d) => { return this.#nScale(d[this.#nKey]); });

        //find all the relevant line data
        let lineData = []
        this.#categories.map(cat => {
            // console.log(this.#data.filter(el => el[this.#categoryKey] == cat))
            lineData.push(this.#data.filter(el => el[this.#categoryKey] == cat && !isNaN(el[this.#nKey])))
        })

        let createuncertaintyLine = (selection, id, key, vertical = true) => {
            selection.append('line')
                // .attr('class', 'uncertainty')
                .attr('data-uncertainty', id)
                // .attr("fill", (d, i) => this.#colourScale(this.#categories[i]))

                .attr("stroke", 'black')
                // .attr("stroke", (d, i) => this.#colourScale(d[this.#categoryKey]))
                .attr('opacity', d => {
                    // console.log(d)
                    if (d[this.#lowerUncertainty] && d[this.#upperUncertainty])
                        return 1
                    else
                        return 0
                })

                .attr('y1', d => vertical ? this.#nScale(d[this.#lowerUncertainty]) : this.#nScale(d[key]))
                .attr('y2', d => vertical ? this.#nScale(d[this.#upperUncertainty]) : this.#nScale(d[key]))
                .attr('x1', d => vertical ? this.#cScales[this.#cScales.length - 1](d[this.#cSeries[this.#cSeries.length - 1]]) : this.#cScales[this.#cScales.length - 1](d[this.#cSeries[this.#cSeries.length - 1]]) - this.#uncertaintyWidth / 2)
                .attr('x2', d => vertical ? this.#cScales[this.#cScales.length - 1](d[this.#cSeries[this.#cSeries.length - 1]]) : this.#cScales[this.#cScales.length - 1](d[this.#cSeries[this.#cSeries.length - 1]]) + this.#uncertaintyWidth / 2)
        }

        //https://observablehq.com/@d3/path-tween
        // function pathTween(lineGen, precision) {
        //     return function(d, k) {
        //         let d1 = lineGen(d)
        //         const path0 = this;
        //         const path1 = path0.cloneNode();
        //         path1.setAttribute("d", d1);
        //         const n0 = path0.getTotalLength();
        //         const n1 = path1.getTotalLength();

        //         // Uniform sampling of distance based on specified precision.
        //         const distances = [0];
        //         const dt = precision / Math.max(n0, n1);
        //         let i = 0;
        //         while ((i += dt) < 1) distances.push(i);
        //         distances.push(1);

        //         // Compute point-interpolators at each distance.
        //         const points = distances.map((t) => {
        //             const p0 = path0.getPointAtLength(t * n0);
        //             const p1 = path1.getPointAtLength(t * n1);
        //             return d3.interpolate([p0.x, p0.y], [p1.x, p1.y]);
        //         });

        //         return (t) => t < 1 ? "M" + points.map((p) => p(t)).join("L") : d1;
        //     };
        // }

        let modifiedSeries = [...this.#cSeries]
        modifiedSeries[modifiedSeries.length - 1] = this.#categoryKey
        let dataMaps = modifiedSeries.map(fv => function(d) { return d[fv] });
        let groupData = d3.rollups(this.#data, v => v, ...dataMaps);

        // console.log("line", lineData)
        // console.log("group", groupData)
        // console.log(this.#categories, this.#cSeries)

        this.#lineGroup
            .selectAll("g[data-layer='0']")
            // .data(lineData)
            .data(groupData)
            .join(
                enter => {
                    let g = enter.append('g')
                        .attr('class', 'line-group')

                        .attr('opacity', 1)
                        .attr('data-layer', 0)
                    // .attr('transform', (d, i) => `translate(${this.#margins.l +300*i}, 0)`)

                    this.#cSeries.map((c, i) => {
                        if (i != 0) {
                            g = g
                                .selectAll('g')
                                .data(d => {
                                    // console.log(d)
                                    return d[1]
                                })
                                .join('g')

                            g
                                .attr('class', 'line-group')
                                .attr('aria-label', d => {
                                    // console.log(d)
                                    return d[0] // key
                                })
                                .attr('data-layer', i)
                                .attr('opacity', 1)
                        }
                    })

                    g
                        .attr('transform', (d, i) => `translate(${this.#calcLineXPos(d[1][0])}, 0)`) //
                        .attr('data-category', (d, i) => this.#categoryLookup[this.#categories[i]])

                    // let path = g.selectAll('path')
                    //     .data(d => d[1])
                    //     .join('path')

                    g.append('path')
                        .datum(d => d[1])
                        // path
                        .attr('class', 'line')
                        .attr('opacity', 1)
                        .attr("fill", "none")
                        .attr("stroke", (d, i) => this.#colourScale(this.#categories[i]))
                        .attr("stroke-width", 4)
                        .style("stroke-dasharray", (d, i) => {
                            // console.log(d)
                            if (!this.#lineTypeSeries) {
                                return 0
                            }
                            if (this.#lineTypeSeries[i] == "dashed") {
                                return 10
                            }
                            else if (this.#lineTypeSeries[i] == "dotted") {
                                return 4
                            }
                            else if (this.#lineTypeSeries[i] == "solid") {
                                return 0
                            }
                        })
                        .attr("d", this.#lineGen)
                        .attr('opacity', 0)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1);

                    if (this.#displayPoints) {
                        // console.log('display points pls')
                        g
                            .selectAll('path.point')
                            .data(d => {
                                // console.log(d)
                                let filterData = d[1].filter(el => !isNaN(el[this.#nKey]))
                                return filterData
                            })
                            .join(
                                enter => {
                                    enter.append('path')
                                        .attr('class', 'point')
                                        .attr('d', d => {
                                            //get the symbol for the category
                                            if (this.#pointTypeSeries)
                                                return this.#pointSymbolMap[this.#categorySymbolMap[d[this.#categoryKey]]](d);
                                            return this.#pointSymbolMap[this.#defaultSymbol](d);
                                        })
                                        .attr("fill", d => this.#colourScale(d[this.#categoryKey]))
                                        .attr("transform", d => {
                                            return `translate(${this.#cScales[this.#cScales.length - 1](d[this.#cSeries[this.#cSeries.length - 1]])}, ${this.#nScale(d[this.#nKey])})`
                                        })
                                        .attr('opacity', 0)
                                        .transition()
                                        .duration(this.#transitionDuration)
                                        .attr('opacity', 1);
                                }
                            )

                    }
                    if (this.#displayUncertainties) {
                        g
                            .selectAll('g.uncertainty')
                            .data(d => d[1].filter(el => !isNaN(el[this.#nKey])))
                            .join(
                                enter => {
                                    let g = enter.append('g')
                                    g
                                        .attr('class', 'uncertainty')
                                        .attr('opacity', 0)
                                        .transition()
                                        .duration(this.#transitionDuration)
                                        .attr('opacity', 1)

                                    createuncertaintyLine(g, 'top', this.#upperUncertainty, false)
                                    createuncertaintyLine(g, 'bottom', this.#lowerUncertainty, false)
                                    createuncertaintyLine(g, 'connector')
                                }
                            )
                    }
                    if (this.#interactive) {
                        g.attr('cursor', 'pointer')
                    }
                },
                update => {
                    update
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1);

                    update.select('path.line')
                        .transition()
                        .duration(this.#transitionDuration)
                        // .style("stroke-dasharray", (d, i) => {
                        //     if (this.#lineTypeSeries[i] == "dashed"){
                        //         return 10
                        //     }
                        //     else if (this.#lineTypeSeries[i] == "dotted"){
                        //         return 4
                        //     }
                        //     else if (this.#lineTypeSeries[i] == "solid"){
                        //         return 0
                        //     }
                        // })
                        .attr("stroke", (d, i) => this.#colourScale(this.#categories[i]))
                        .attrTween("d", this.#pathTween(this.#lineGen, 4))

                    if (this.#displayPoints) {
                        update
                            .selectAll('path.point')
                            .data(d => d.filter(el => !isNaN(el[this.#nKey])))
                            .join(
                                enter => {
                                    enter.append('path')
                                        .attr('class', 'point')
                                        .attr('d', d => {
                                            //get the symbol for the category
                                            if (this.#pointTypeSeries)
                                                return this.#pointSymbolMap[this.#categorySymbolMap[d[this.#categoryKey]]](d);
                                            return this.#pointSymbolMap[this.#defaultSymbol](d);
                                        })
                                        .attr("fill", d => this.#colourScale(d[this.#categoryKey]))
                                        .attr("transform", d => `translate(${this.#cScale(d[this.#cKey])}, ${this.#nScale(d[this.#nKey])})`)
                                        .attr('opacity', 0)
                                        .transition()
                                        .duration(this.#transitionDuration)
                                        .attr('opacity', 1);
                                },
                                update => {
                                    update
                                        .transition()
                                        .duration(this.#transitionDuration)
                                        .attr('d', d => {
                                            //get the symbol for the category
                                            if (this.#pointTypeSeries)
                                                return this.#pointSymbolMap[this.#categorySymbolMap[d[this.#categoryKey]]](d);
                                            return this.#pointSymbolMap[this.#defaultSymbol](d);
                                        })
                                        .attr("fill", d => this.#colourScale(d[this.#categoryKey]))
                                        .attr("transform", d => {
                                            return `translate(${this.#cScale(d[this.#cKey])}, ${this.#nScale(d[this.#nKey])})`;
                                        })
                                        .attr('opacity', 1);
                                },
                                exit => {
                                    exit
                                        .transition()
                                        .duration(this.#transitionDuration)
                                        .attr('opacity', 0)
                                        .remove()
                                }
                            )

                    }
                    if (this.#displayUncertainties) {
                        update
                            .selectAll('g.uncertainty')
                            .data(d => d.filter(el => !isNaN(el[this.#nKey])))
                            .join(
                                enter => {
                                    let g = enter.append('g')
                                    g
                                        .attr('class', 'uncertainty')
                                        .attr('opacity', 0)
                                        .transition()
                                        .duration(this.#transitionDuration)
                                        .attr('opacity', 1)

                                    createuncertaintyLine(g, 'top', this.#upperUncertainty, false)
                                    createuncertaintyLine(g, 'bottom', this.#lowerUncertainty, false)
                                    createuncertaintyLine(g, 'connector')
                                },
                                update => {


                                    this.#updateUncertaintyLine(update.select(`line[data-uncertainty='top']`), this.#upperUncertainty, false)
                                    this.#updateUncertaintyLine(update.select(`line[data-uncertainty='bottom']`), this.#lowerUncertainty, false)
                                    this.#updateUncertaintyLine(update.select(`line[data-uncertainty='connector']`))
                                },
                                exit => {
                                    exit
                                        .transition()
                                        .duration(this.#transitionDuration)
                                        .attr('opacity', 0)
                                        .remove()
                                }
                            )
                    }
                },
                exit => {
                    // console.log('exit', exit)
                    exit
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)
                        .remove()
                }
            )
    }
    #renderTitles() {
        // Create subgroup 
        if (!this.#titleGroup)
            this.#titleGroup = this.#container.append('g').attr('class', 'titles')

        const titles = this.#titleGroup

        const graphTitle = titles.select('.graph-title')

        // Render chart title
        if (graphTitle.empty()) {
            //add title
            titles
                .append('text')
                .attr('class', 'graph-title')
                .attr('x', (this.#width - this.#margins.r) / 2)
                .attr('y', this.#margins.t / 2)
                .attr('dy', 0)
                .attr('opacity', 1)
                .attr('text-anchor', 'middle')
                .text(this.#graphTitle)
            // .call(this.#wrap, this.#width)
        }
        else if (graphTitle.text() !== this.#graphTitle) {
            //transition existing title to new title
            graphTitle
                .attr('opacity', 0)
                .text(this.#graphTitle)
            // .call(this.#wrap, this.#width)
            graphTitle
                .transition()
                .duration(this.#transitionDuration)
                .attr('opacity', 1)
            // .transition()
            // .duration(this.#transitionDuration / 2)
            // .attr('opacity', 0)
            // .on('end', () => {
            //   graphTitle.text(this.#graphTitle)

            //   graphTitle
            //     .transition()
            //     .duration(this.#transitionDuration / 2)
            //     .attr('opacity', 1)
            // })
        }


        const height = this.#height;
        const v = 'n'
        const vTitle = this.#nAxisTitle
        const vSpacing = this.#nAxisTitleSpacing
        const vAxis = titles.select(`.${v}-axis-title`)
        const vtAxisLength = height + this.#margins.t - this.#margins.b

        // Render axis titles
        if (vAxis.empty()) {
            titles
                .append('text')
                .attr('class', v + '-axis-title')
                .attr('opacity', 1)
                .attr('x', (-height - this.#margins.t + this.#margins.b) / 2)
                .attr('y', () => {
                    return this.#margins.l - vSpacing;
                })
                .attr('dy', 0)
                .attr('transform', `rotate(-90)`)
                .attr('text-anchor', 'middle')
                .attr('alignment-baseline', v == 'c' ? "after-edge" : null)
                .text(vTitle)
                .call(this.#wrap, vtAxisLength - vtAxisLength * 0.2)
        }
        else if (vAxis.text() !== vTitle) {

            vAxis
                .attr('opacity', 0)
                .text(vTitle)
            vAxis
                .transition()
                .duration(this.#transitionDuration)
                .attr('opacity', 1)
        }

        const s = 's'
        const sTitle = this.#secondaryNTitle
        const sSpacing = this.#secondaryNTitleSpacing
        const sAxis = titles.select(`.${s}-axis-title`)

        // Render axis titles
        if (sAxis.empty()) {
            titles
                .append('text')
                .attr('class', v + '-axis-title')
                .attr('opacity', 1)
                .attr('x', (-height - this.#margins.t + this.#margins.b) / 2)
                .attr('y', () => {
                    return this.#width - this.#margins.r + sSpacing;
                })
                .attr('transform', `rotate(-90)`)
                .attr('text-anchor', 'middle')
                .attr('alignment-baseline', v == 'c' ? "after-edge" : null)
                .text(sTitle);
        }
        else if (sAxis.text() !== sTitle) {

            sAxis
                .attr('opacity', 0)
                .text(sTitle)
            sAxis
                .transition()
                .duration(this.#transitionDuration)
                .attr('opacity', 1)
        }

        const h = 'c'
        const hTitle = this.#cAxisTitle
        const hSpacing = this.#cAxisTitleSpacing
        const hAxis = titles.select(`.${h}-axis-title`)

        if (hAxis.empty()) {
            titles
                .append('text')
                .attr('class', h + '-axis-title')
                .attr('opacity', 1)
                .attr('x', (this.#width - this.#margins.r + this.#margins.l) / 2)
                .attr('y', height - this.#margins.b + hSpacing)
                .attr('text-anchor', 'middle')
                .attr('alignment-baseline', h == 'c' ? "before-edge" : null)
                .text(hTitle);
        }
        else if (hAxis.text() !== hTitle) {
            hAxis
                .attr('opacity', 0)
                .text(hTitle)
            hAxis
                .transition()
                .duration(this.#transitionDuration)
                .attr('opacity', 1)
            // hAxis
            //   .transition()
            //   .duration(this.#transitionDuration / 2)
            //   .attr('opacity', 0)
            //   .on('end', () => {
            //     hAxis.text(hTitle)
            //     hAxis
            //       .transition()
            //       .duration(this.#transitionDuration / 2)
            //       .attr('opacity', 1)
            //   })
        }
    }
    #renderLegend() {
        if (this.#legendGroup) {
            this.#legendGroup
                .transition()
                .duration(this.#transitionDuration)
                .attr('transform', `translate(${this.#legendPosition[0]}, ${this.#legendPosition[1]})`)
        }

        if (!this.#legendGroup) {
            this.#legendGroup = this.#container.append('g')
                .attr('class', 'legend')
                .attr('transform', `translate(${this.#legendPosition[0]}, ${this.#legendPosition[1]})`)
        }


        this.#legendGroup
            .selectAll('g')
            .data(this.#categories)
            .join(
                enter => {
                    let lineLength = this.#legendLineLength;
                    let textOffset = this.#legendSpacing[0]
                    let legendIntervalSpacing = this.#legendSpacing[1];

                    let g = enter.append('g');
                    g
                        .attr('class', d => 'legend-group selected')
                        .attr('data-category', (d, i) => this.#categoryLookup[d])
                        .attr('transform', (d, i) => `translate(${this.#legendOrientation == "h" ? legendIntervalSpacing * i : 0}, ${this.#legendOrientation == "v" ? legendIntervalSpacing * i : 0})`)
                        .attr('opacity', 0)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1)

                    g.append('line')
                        .attr("stroke", (d, i) => this.#colourScale(d))
                        .attr("stroke-width", 4)
                        .attr("x1", 0)
                        .attr("y1", 0)
                        .attr("x2", lineLength)
                        .attr("y2", 0)
                        .style("stroke-dasharray", (d, i) => {
                            if (!this.#lineTypeSeries) {
                                return 0
                            }
                            if (this.#lineTypeSeries[i] == "dashed") {
                                return 10
                            }
                            else if (this.#lineTypeSeries[i] == "dotted") {
                                return 4
                            }
                            else if (this.#lineTypeSeries[i] == "solid") {
                                return 0
                            }
                        })

                    let text = g.append('text')
                        .attr('x', lineLength + textOffset)
                        .attr('y', 0)
                        .attr('dy', 0)
                        .attr('alignment-baseline', 'middle')
                        .attr('opacity', 1)
                        .html(d => d)

                    //wrap legend text
                    if (this.#legendTextWrapWidth && text.node() && text.node().getComputedTextLength() > this.#legendTextWrapWidth) {
                        // console.log(text.node().getComputedTextLength(), this.#legendTextWrapWidth)
                        text.call(this.#wrap, this.#legendTextWrapWidth)
                        text.call(this.#centerTSpans)
                    }

                    if (this.#displayPoints) {
                        g.append('path')
                            .attr('d', d => {
                                //get the symbol for the category
                                // console.log(this.#categorySymbolMap[d])
                                if (this.#pointTypeSeries) {
                                    return this.#pointSymbolMap[this.#categorySymbolMap[d]](d)
                                }
                                return this.#pointSymbolMap[this.#defaultSymbol](d);
                            })
                            .attr("fill", d => this.#colourScale(d))
                            .attr("transform", d => `translate(${lineLength/2}, 0)`)
                    }

                    if (this.#interactive) {
                        g.attr('cursor', 'pointer')
                    }
                },
                update => {
                    let lineLength = this.#legendLineLength;
                    let textOffset = this.#legendSpacing[0]
                    let legendIntervalSpacing = this.#legendSpacing[1];

                    update
                        .attr('class', d => 'legend-group selected')
                        .attr('data-category', (d, i) => this.#categoryLookup[d])
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('transform', (d, i) => `translate(${this.#legendOrientation == "h" ? legendIntervalSpacing * i : 0}, ${this.#legendOrientation == "v" ? legendIntervalSpacing * i : 0})`)
                        .attr('opacity', 1)


                    update.select('line')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr("stroke", (d, i) => this.#colourScale(d))
                        .attr("x2", lineLength)

                    let text = update.select('text')

                    text
                        .attr('opacity', function(d) {
                            //will need some logic to check if check is equal for wrapped text (tspan join)
                            let selection = d3.select(this)
                            if (selection.text() == d) {
                                return selection.attr('opacity');
                            }
                            return 0;
                        })
                        .html(d => d)
                    // console.log(text)
                    // if (this.#legendTextWrapWidth && text.node().getComputedTextLength() > this.#legendTextWrapWidth) {
                    //     console.log(text.node().getComputedTextLength(), this.#legendTextWrapWidth)
                    //     text.call(this.#wrap, this.#legendTextWrapWidth)
                    // }

                    text
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('x', lineLength + textOffset)
                        .attr('opacity', 1)

                },
                exit => {
                    exit
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)
                        .remove()
                }
            )
    }
    #findSelectedCategories(dataCategory = true) {
        let selectedValues = [];
        this.#container.select('.legend').selectAll(`g.selected`).each(function(d) {
            let current = d3.select(this);
            if (dataCategory) {
                selectedValues.push(current.data()[0])
            }
            else {
                selectedValues.push(current.attr('data-category'))
            }

        })
        return selectedValues;
    }
    #addInteraction() {
        const that = this;
        this.#selectedCategories = this.#findSelectedCategories();

        let fadeLegendCenter = (category, group) => {
            //fade out legend group and unselect it
            let gSelection = group ? group : this.#legendGroup.select(`g[data-category='${category}']`)
            gSelection
                // .attr("opacity", 1)
                .transition()
                .duration(this.#transitionDuration)
                .attr("opacity", 0.5);

            gSelection
                .classed('selected', false);

            this.#selectedCategories = this.#findSelectedCategories();
        }

        let reverseFadeCenter = (category, group) => {
            //fade in legend group and select it
            let gSelection = group ? group : this.#legendGroup.select(`g[data-category='${category}']`)
            gSelection
                .transition()
                .duration(this.#transitionDuration)
                .attr("opacity", 1);

            gSelection
                .classed('selected', true);

            this.#selectedCategories = this.#findSelectedCategories();
        }

        let removeLine = (category, group) => {
            let lineSelection = group ? group : this.#lineGroup.selectAll(`g[data-category='${category}']`);

            lineSelection
                .transition()
                .duration(this.#transitionDuration)
                .attr('opacity', 0)
        }

        let addLine = (category, group) => {
            let lineSelection = group ? group : this.#lineGroup.select(`g[data-category='${category}']`);

            lineSelection
                .transition()
                .duration(this.#transitionDuration)
                .attr('opacity', 1)
        }

        // //or update selected lines
        let updateSelectedLines = (category, group) => {
            that.#findSelectedCategories(false).map(cat => {
                let g = this.#lineGroup.selectAll(`g[data-category='${cat}']`)
                g
                    .transition()
                    .duration(this.#transitionDuration)
                    .attr('opacity', 1)
                g.selectAll('path.line')
                    .transition()
                    .duration(this.#transitionDuration)
                    .attrTween("d", this.#pathTween(this.#lineGen, 4))

                if (this.#displayPoints) {
                    g.selectAll('path.point')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr("transform", d => {
                            return `translate(${this.#cScales[this.#cScales.length - 1](d[this.#cSeries[this.#cSeries.length - 1]])}, ${this.#nScale(d[this.#nKey])})`
                        })
                }

                if (this.#displayUncertainties) {
                    console.log(g.select(`line[data-uncertainty='top']`))
                    g.selectAll('g.uncertainty').each(function(d) {
                        // console.log(d, this)
                        let uncertaintyGroup = d3.select(this)

                        that.#updateUncertaintyLine(uncertaintyGroup.select(`line[data-uncertainty='top']`), that.#upperUncertainty, false)
                        that.#updateUncertaintyLine(uncertaintyGroup.select(`line[data-uncertainty='bottom']`), that.#lowerUncertainty, false)
                        that.#updateUncertaintyLine(uncertaintyGroup.select(`line[data-uncertainty='connector']`))
                    })

                }
            })
        }

        let updateNAxis = () => {
            //reinitialize all the nAxis variables to accomodate the removed bars, and update it
            this.initNScale(false);

            let nAxisOptions = {};
            let cAxisOptions = {};
            let sAxisOptions = {};
            if (this.#gridlines) {
                const gridHeight = this.#height - this.#margins.b - this.#margins.t;
                const gridWidth = this.#width - this.#margins.l - this.#margins.r;
                const gridlineLength = -gridWidth

                nAxisOptions["tickSizeInner"] = gridlineLength
                nAxisOptions["tickPadding"] = 10
            }
            if (this.#cAxisTickSkip > 0) {
                cAxisOptions['tickValues'] = this.#cScale.domain().filter((d, i) => i % this.#cAxisTickSkip === 0)
            }

            this.initAxes(cAxisOptions, nAxisOptions, sAxisOptions);
            this.#updateAxes();

            // //update local reference to the nScale
            // nScale = this.#nScale;
        }

        let isolated = false;
        let categoriesBeforeCollapse = []
        let cIndex = this.#cSeries.length - 1;



        //line listeners
        // this.#lineGroup.selectAll('.line-group')
        this.#lineGroup.selectAll(`g[data-layer='${cIndex}']`).on('click', function(e, d) {
            // console.log(this)
            //set what groups were there before isolating to the clicked line
            if (isolated == false)
                categoriesBeforeCollapse = that.#findSelectedCategories(false);

            let clickedGroup = this;
            let clickedDataCategory = d3.select(clickedGroup).attr('data-category');
            let allLines = that.#lineGroup.selectAll(`g[data-layer='${cIndex}']`)

            //loop through all lines
            allLines.each(function(d, i) {
                let currSelection = d3.select(this);
                let currDataCat = currSelection.attr('data-category');
                //if not the one that was clicked
                // if (this != clickedGroup) {
                if (clickedDataCategory != currDataCat) {
                    //add hidden group back
                    if (isolated && categoriesBeforeCollapse.includes(currDataCat)) {
                        reverseFadeCenter(currDataCat)
                        // updateNAxis()
                        // addLine(null, currSelection)
                    }
                    //remove group
                    else {
                        fadeLegendCenter(currDataCat)
                        // updateNAxis()
                        removeLine(null, currSelection)
                    }
                }
            })
            isolated = !isolated;
            updateNAxis()
            updateSelectedLines()
        })

        //legend listeners
        this.#legendGroup.selectAll('.legend-group').on('click', function(e, d) {
            isolated = false;
            let clickedG = d3.select(this);
            let dataCat = clickedG.attr('data-category');
            //remove group
            if (clickedG.classed('selected')) {
                fadeLegendCenter(null, clickedG)
                updateNAxis()
                removeLine(dataCat)
                updateSelectedLines()
            }
            //add group
            else {
                reverseFadeCenter(null, clickedG) //clickedG.attr('data-category')
                updateNAxis()
                // addLine(dataCat)
                updateSelectedLines()
            }
        })

    }
    #addHoverFadeout() {
        let that = this;
        let cIndex = this.#cSeries.length - 1;

        this.#lineGroup.selectAll(`g[data-layer='${cIndex}']`)
            .on('mouseover', function(d) {
                let selectedLines = that.#findSelectedCategories(false);
                // console.log(selectedLines)
                let current = d3.select(this)
                let otherGroups = that.#lineGroup.selectAll('.line-group').filter(function(el) {
                    return d3.select(this).attr('data-category') != current.attr('data-category') && selectedLines.includes(d3.select(this).attr('data-category'))
                })
                otherGroups.attr('opacity', 0.3)
            })
            .on('mouseout', function(d) {
                let selectedLines = that.#findSelectedCategories(false);
                let otherGroups = that.#lineGroup.selectAll('.line-group').filter(function(el) {
                    return selectedLines.includes(d3.select(this).attr('data-category'))
                })

                otherGroups.attr('opacity', 1)
            })

        this.#legendGroup.selectAll('.legend-group')
            .on('mouseover', function(d) {
                let selectedLines = that.#findSelectedCategories(false);
                let current = d3.select(this)
                let otherGroups = that.#lineGroup.selectAll('.line-group').filter(function(el) {
                    return d3.select(this).attr('data-category') != current.attr('data-category') && selectedLines.includes(d3.select(this).attr('data-category'))
                })
                otherGroups.attr('opacity', 0.3)
            })
            .on('mouseout', function(d) {
                let selectedLines = that.#findSelectedCategories(false);
                let otherGroups = that.#lineGroup.selectAll('.line-group').filter(function(el) {
                    return selectedLines.includes(d3.select(this).attr('data-category'))
                })
                otherGroups.attr('opacity', 1)
            })
    }
    #setTabbing() {
        const container = this.#container;
        const lines = this.#container.select(".lines");

        container
            .on('keydown', (e) => {
                const isContainer = e.target.id == container.attr('id');
                //find which legend values are toggled on or off
                let selectedCategories = this.#findSelectedCategories(false);
                let selectedChildren = lines.selectAll(".line-group").filter(function(d) {
                    return selectedCategories.includes(d3.select(this).attr('data-category'))
                })
                // console.log('sc', selectedChildren)
                // console.log(e)
                let targetSelection = d3.select(e.target);

                if (e.key == 'Enter') {
                    //begin inner tabbing between regions
                    // console.log(isContainer)
                    if (isContainer) {

                        if (!selectedChildren.empty()) {
                            console.log(selectedChildren.node())
                            selectedChildren
                                .attr('tabindex', 0);
                            selectedChildren.node().focus(); //first child
                        }
                    }
                    else {
                        let selection = d3.select(e.target)
                        selection.dispatch('click')
                    }
                }
            })
    }
    #wrap(text, width) {
        let splitRegex = /\s+/;

        text.each(function() {
            var text = d3.select(this),
                words = text.text().split(splitRegex).reverse(),
                word,
                line = [],
                lineNumber = 0,
                lineHeight = 1.1, // ems
                x = text.attr("x") ?? 0,
                y = text.attr("y") ?? 0,
                dy = parseFloat(text.attr("dy")) ?? 0,
                tspan = text
                .text(null)
                .append("tspan")
                .attr("x", x)
                .attr("y", y)
                .attr("dy", dy + "em");

            //loop through the words and add them to a tspan
            while ((word = words.pop())) {
                line.push(word)
                let lineJoin = line.join(" ")
                tspan.text(lineJoin) // make array a sentence based on last split. If only one word in line array, then stays one word

                //if sentence is now too big for width, you've added too many words / word itself is too large. Modify to be under the width then render the tspan
                if (tspan.node().getComputedTextLength() > width) {

                    //means the word alone is too long, so modify the font size until it fits. remove / modify this section if we don't want text shrinking
                    if (line.length <= 1) {
                        let fontSize = parseFloat(window.getComputedStyle(tspan.node(), null)["fontSize"])
                        //go down a font-size until it fits
                        while (tspan.node().getComputedTextLength() > width && fontSize > 0) {
                            fontSize = parseFloat(window.getComputedStyle(tspan.node(), null)["fontSize"]);
                            tspan.attr('font-size', `${fontSize - 1}px`)
                        }
                        text.selectAll('tspan').attr('font-size', `${fontSize - 1}px`)
                        text.attr('font-size', `${fontSize - 1}px`)
                    }
                    //else there's a sentence. Make the sentence shorter by putting the last word of the line back on the word list
                    else {
                        words.push(line.pop());
                        lineJoin = line.join(" ")
                        tspan.text(lineJoin);
                    }
                    //make the next tspan if there are still words left and reset whats in a line
                    if (words.length != 0) {
                        tspan = text
                            .append("tspan")
                            .attr('font-size', text.attr('font-size')) // remove if we don't want text shrinking. gets font-size from parent text element if it exists
                            .attr("x", x)
                            .attr("y", y)
                            .attr("dy", ++lineNumber * lineHeight + dy + "em")

                        line = []
                    }

                }
                //if there are no more words to loop through, then render the last joined words
                if (words.length == 0) {
                    tspan
                        .text(lineJoin);
                }
            }
        });
    }
    #centerTSpans(text) {
        text.each(function() {
            let text = d3.select(this)
            let tspans = text.selectAll('tspan')
            let bounds = this.getBBox()
            let fontSize = parseFloat(window.getComputedStyle(tspans.node(), null)["fontSize"]);

            text.attr("transform", `translate(0,${-bounds.height/2 + fontSize})`)
        })
    }
    #addTable() {
        let data = this.#data;
        // console.log('tableData', this.#data)
        /* 
          Adds a table to the #table property. Contains the standard classes typically used on infobase products.
          
          Note: uses #table, #tableSummary, #tableDetails, #data, #cSeries, #categories
        */

        const tableExists = !this.#table.select('details').empty();

        let tableDetails;

        if (tableExists) {
            this.#table.select('details').selectAll("*").remove();
            tableDetails = this.#table.select('details');
        }
        else {
            tableDetails = this.#table.append('details');
        }

        // let tableID = this.#table.attr('id') + "-table";


        tableDetails.append("summary").text(this.#tableSummary)
        const tableContainer = tableDetails.append("div").attr("class", "table-responsive")
        const table = tableContainer.append("table")
            // .attr('id', tableID)
            .attr("class", "wb-table table table-bordered table-striped table-hover")

        if (this.#tableCaption)
            table.append('caption').text(this.#tableCaption)
        const tr = table.append('thead').append('tr').attr('class', 'bg-primary')
        // let tableArr = this.#data.columns;
        let tableArr = [...this.#cSeries]
        if (this.#categoryKey) {
            tableArr.push(this.#categoryKey)
        }
        tableArr.push(this.#nKey)
        if (this.#displayUncertainties) {
            tableArr.push(this.#upperUncertainty)
            tableArr.push(this.#lowerUncertainty)
        }
        // tableArr.push(this.#cKey)
        // tableArr = tableArr.concat(this.#categories)

        tableArr.map(el => {
            tr.append('th')
                // .style("vertical-align", "top").attr('scope', 'col')
                .text(() => {
                    return this.#tableHeaderFunction ? this.#tableHeaderFunction(el) : el
                })
        })

        const tbody = table.append("tbody")

        this.#data.map(row => {
            let tr = tbody.append("tr")

            tableArr.map(el => {
                tr.append('td').text(row[el])
            })
        })

        let language = d3.select('html').attr('lang');
    	if (language == 'en'){
    		$(table.node()).DataTable();
    	}
    	else{		
				$(table.node()).DataTable({
					"language": {
						"sProcessing":     "Traitement en cours...",
						"sSearch":         "Rechercher&nbsp;:",
						"sLengthMenu":     "Afficher _MENU_ &eacute;l&eacute;ments",
						"sInfo":           "Affichage de l'&eacute;lement _START_ &agrave; _END_ sur _TOTAL_ &eacute;l&eacute;ments",
						"sInfoEmpty":      "Affichage de l'&eacute;lement 0 &agrave; 0 sur 0 &eacute;l&eacute;ments",
						"sInfoFiltered":   "(filtr&eacute; de _MAX_ &eacute;l&eacute;ments au total)",
						"sInfoPostFix":    "",
						"sLoadingRecords": "Chargement en cours...",
						"sZeroRecords":    "Aucun &eacute;l&eacute;ment &agrave; afficher",
						"sEmptyTable":     "Aucune donn&eacute;e disponible dans le tableau",
						"oPaginate": {
							"sFirst":      "Premier",
							"sPrevious":   "Pr&eacute;c&eacute;dent",
							"sNext":       "Suivant",
							"sLast":       "Dernier"
						},
						"oAria": {
							"sSortAscending":  ": activer pour trier la colonne par ordre croissant",
							"sSortDescending": ": activer pour trier la colonne par ordre d&eacute;croissant"
						}
					},
				});
				table.on('click', 'th', function() {
					let tableID = table.attr('id');
					$("#" + table.attr('id') + " th").addClass("sorting")
					//$(this).removeClass("sorting")
				});			
		}
    }
}
"""
        documentation = """## LineGraph Class

The aim of this class is to quickly create 
reusable line graphs. Your job is to just send 
in the right data and style the graph with built in parameters or custom CSS.

### Quickstart

First, create an `index.html` file and `main.js` 
file. For this example, they are made in the same directory. 
- For the HTML file, ensure 
  you have a div whose only child is an SVG element.
- Also **ensure that you load the `d3.js` v7 library 
  and `main.js` as a module** (in that order).
- `main.js` represents YOUR js file that you wish to use the modules in.
- Example:

```
(index.html)
--------------------
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Line chart</title>
    <link href="/src/css/modular/main.css" rel="stylesheet" type="text/css">
</head>
<body>
<body>
  <figure>
    <figcaption class="h3">Figure title</figcaption>
    <div id='wrapper1'>
      <svg id='line1'></svg>
    </div>
  </figure>
</body>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="/src/js/functions/localization.js"></script>
<script src='./main.js' type='module'></script>

</html>
```

Next, import `LineGraph` from `line.js` in `main.js`. 
Can use this code as an example in `main.js` to 
set the basics for the graph.

```
(main.js)
---------------------
import { LineGraph } from "/src/js/modular/line.js";

```

Now, add some more code to `main.js` to load the data you want.

**Example data format**
```
YEAR,VALUE,PT
2017,472.539,AB
2018,451.605,AB
2019,408.184,AB
2020,337.221,AB
2021,331.267,AB
2022,347.431,AB
2017,604.893,BC
2018,576.586,BC
2019,501.259,BC
2020,411.774,BC
2021,405.486,BC
2022,426.259,BC
2017,931.953,MB
2018,957.686,MB
2019,725.151,MB
2020,725.319,MB
2021,534.909,MB
2022,606.586,MB
```

Read in your data. This is one example of how to do it,
which lets you read in multiple csv and json files at once.

```
(main.js)
---------------------
// Load data, datafiles can contain multiple
let dataFiles = [
    '/src/data/yourProject/YOURDATAHERE.csv', // 0
]
let promises = [];
dataFiles.forEach(function(url) {
    if (url.match(/.*\.csv$/gm)) {
        promises.push(d3.csv(url))
    }
    else if (url.match(/.*\.json$/gm)) {
        promises.push(d3.json(url))
    }
});
Promise.all(promises).then(function(values) {
    console.log('myData', values) // values is an array of the data you loaded in.
    
    // Data is done being read in. Let's give it to a function to build it.
    buildLinechart(values[0])
})
```

Time to make a linechart! We'll set this up in it's own function that we referenced earlier.

```
(main.js)
---------------------
function buildLinechart(data){
  
    // Setup, table not required, margins
    const Line = new LineGraph();
    Line
      .wrapper(d3.select('div#wrapper1'))
      .container(d3.select('svg#line1'))
      .table(d3.select('div#wrapper1'))
      .margins([60, 60, 100, 100])
    
    //set data and keys within it
      .data(data)
    //Categorical series, column(s) in data that contains the independant variables (xAxis). 
      .cKey('YEAR')
    // Numerical key. Represents the "y" or dependent variable
      .nKey('VALUE')
      
      .categoryKey('PT') // Seperation in different lines. What will be shown in the legend.
    
    // Set titles as needed, all optional
      .graphTitle('Graph title') //would recommend using a figcaption instead
      .nAxisTitle('nAxis')
      .cAxisTitle('cAxis')
      
    // Set different boolean options. More options below
      .displayLegend(true)
      .grouped(true) // if false, is stacked
      
    // Legend options, more customization below
      .legendPosition([400, 50])
    
    // Initiliase scales, axes, generators, etc. Init and render are seperate calls incase an override of initialized variables is desired before render.
      .init()
    
    // Render the linegraph
      .render();
}
```

## CSS

The linechart within the container is setup with classes. Use the inspector to see the format, 
but common uses are:
- *Lines*: `svg#line1 g.lines` contains a subgroup for each series of data
  you have. For instance, it may contain `g.val0` and `g.val1`
  (if you set those values in your ySeries array). Each of these subgroups 
  will have `rect` elements whose fill you can change. 
- *Titles*: `svg#line1 g.titles` contains three text elements 
  which represent the graph title (`text.graph-title`), 
  y-axis title (`text.n-axis-title`), and x-axis title 
  (`text.c-axis-title`).
- *Axes*: `svg#line1>g.axes>g.y text` - all the text in the 
  y-axis. Similarly, `svg#line1>g.axes>g.x text` selects 
  all the text in the x-axis.
- *Legend*: `svg#line1>g.legend` contains a `circle` and `text` element
  per output series that you have. Each will have a class based on 
  the values you set in your ySeries array. Ex: You might have 
  elements like `text.var0` and `circle.var1`.
- *Tooltip*: `div#wrapper1>div.tooltip` is the tooltip element. You
  will likely want to change its size, background colour, etc. 


## Additional methods and attributes

To **change colours** you can set the Line.colourSeries to a new array of desired colours.
 - `line.colourSeries(['blue', 'red', 'yellow'])`
This assigns the colours in order, such that `val0` is coloured `blue`, `val1` is coloured `red`, etc.

There are many other common ways to customize the line graph listed below. These boolean values control whether that functionality appears, but are defaulted to false (mostly):
 - *gridlines*: `line.gridlines(true);`
 - *displayPoints*: `line.displayPoints(true);`
 - *hideLines*: `line.hideLines(true);`
 - *displayUncertainties*: `line.displayUncertainties(true);`
    - Requires the lower and upper uncertainty values to be set
 - *interactive*: `line.interactive(true);`
 - *hoverFade*: `line.hoverFade(true);`
 - *fitTickText*: `line.fitTickText(true);`
    - Fits the cAxis tick text within the cScale.step()
 - *Table caption above*: `line.captionAbove(true);`

Customize the spacing, sizes:
 - *Height*: `line.height(480);`
 - *Width*: `line.width(720);`
    - Width of the SVG will always be 100% of the container. The height and width attributes are the viewbox ratio of the SVG.
 - *Margins [Top, right, bottom, left]*: `line.margins([80,40,120,100]);`
 - *c-Axis-title distance from axis*: `line.cAxisTitleSpacing(50);`
 - *n-Axis-title distance from axis*: `line.nAxisTitleSpacing(60);`

Customize the legend:
 - *legendSpacing [x,y]*: `line.legendSpacing([15, 22]);`
    - x: Represents the text offset between the symbol and the label
    - y: Represents the space between full legend elements 
 - *legendPosition [x,y]*: `line.legendPosition([550, 100]);`
 - *legendOrientation*: `line.legendOrientation('v');`
    - Accepts either `h` or `v` for horizontal and vertical respectively
 - *Length of line*: `line.legendLineLength(50);`
 - *Label wrap width (px)*: `line.legendTextWrapWidth(200);`

Customizing the line size, texture, points:
 - *lineWidth*: `line.lineWidth(4);`
 - *lineTypeSeries*: `line.lineTypeSeries(480);`
 - *pointTypeSeries*: `line.pointTypeSeries(480);`
 - *pointSize*: `line.pointSize(100);`

Uncertainty lines:
 - *Upper uncertainty*: `line.upperUncertainty('upperKey');`
    - Key of the column name contianing the value for the upper uncertainty
 - *Lower uncertainty*: `line.lowerUncertainty('lowerKey');`
    - Key of the column name containing the value for the lower uncertainty
 - *Uncertainty width (pixels)*: `line.uncertaintyWidth(8);`

Customize formatting/misc.:
 - *How many decimals to round off to*: `line.decimalPlaces(1)`
 - *Transition duration*: `line.transitionDuration(1000)`

Formatting functions *yourFormattingFunction referenced below* (overwrites any other formatting that would be handled by the code):
 - *tableHeaderFunction*: `line.tableHeaderFunction(yourFormattingFunction)`
    - `d`: The value of the raw table header
    - `return`: The value you want to display in its stead
 - *nTickFormat*: `line.nTickFormat(yourFormattingFunction)`
    - `d`: The number from the tick
    - `return`: The value you want to display in its stead
 - *cTickFormat*: `line.cTickFormat(yourFormattingFunction)`
    - `d`: The value from the tick
    - `return`: The value you want to display in its stead

*Tip*: Unless you're doing a very custom format, you can use d3.format() with any of those options as well instead of yourFormattingFunction

```
(main.js)
---------------------
function yourFormattingFunction(d){
  console.log(d) // d is the data used to create the element being interacted with.
  
  let yourValue;
  
  //do whatever you want
  
  return yourValue;
}
```

Accessibility:
 - *Aria figure label*: `line.figureAriaLabel("linegraph")`
 - *Aria figure description*: `line.figureAriaDescription('Your description. Default is generic how to use.')`

Create/customize the table:
 - *Create table in div*: `line.table(d3.select('div#wrapper1'))`
 - *Caption*: `line.tableCaption('Example caption')`
 - *Summary*: `line.tableSummary('Example - Text description')`
 - *Table placement*: `line.captionAbove(true);`
    - Places the caption above the data table functions (search, pagination, etc) instead of within


## OVERWRITING THE INIT :)
`CAUTION`: things may break

The init() and render() are seperate. This is because if you want to, you can overwrite many of the fundamental parts of the code.

Specifically, init() setups these things in this order:
 - *Container*: `initCategories()`
 - *initCategories*: `initCategories()`
 - *initSymbols*: `initSymbols()`
 - *initNScale*: `initNScale()`
 - *initCScale*: `initCScale()`
 - *initSecondaryScale*: `initSecondaryScale()`
 - *initColourScale*: `initColourScale()`
 - *initAxes*: `initAxes()`

#Overwrite examples

*nScale domain overwrite*
I want to make it so that the linechart has values from 0 to 100 in it. So, I need to overwrite the domain of the nScale. This can be done in one line.

```
(main.js)
---------------------
line
  
  // setup the linechart
  
  .init()
  .nScale(line.nScale().domain([0, 100])) // get the nScale, overwrite the domain, set it as the nScale
  .render();
```

*cScale full overwrite*
The line code does not currently support having a time scale, but you can still make one by overwriting it.

```
(main.js)
---------------------
line
  // setup the linechart. Data values you're plotting will need to be valid with the new scale, so parse them to dates
  .init()

// get the scale you want to replace
let scale = line.cScale();

// create the scale you want to insert
let newScale = d3.scaleTime()
	.domain([new Date("2020-01-01"), new Date("2020-12-31")])
	.range(scale.range()) // use the old scales range
    
line
	.cScale(newScale) //set the new cScale for the line
	.initAxes() //need to reinitialize the axes, as it uses the cScale.
    
line
  .render();
```"""
    elif graph_type == 'map':
        source = """export class Map {
    //FIELDS
    #wrapper;
    #container;
    #ptGroup;
    #rvGroup;
    #invisGroup;
    #legendGroup;
    #canadaGroup;
    #markerGroup;

    //region identifiers
    #regionId = "PRUID";
    #regionName = "PRENAME";
    #markerRegionId = "Province";

    //
    #hasRendered = false;

    //toggles
    #interactive = false;
    #displayValues = false;
    #tooltips = false;
    #suppressed = false;
    #notApplicable = false;
    #percent = false;
    #canadaBubble = false;
    #zoomable = false;
    #SINotation = false;
    #legendGradient = false;
    #recalculateLegendIntervals = false;
    
    #regionValueOpacity = 1;

    #legendGradientScale;

    #autoTabClick = true;

    #numberSeperator = ",";
    #numberFormat;
    #defaultNumberFormat = d3.format(",");


    #canadaValue;
    #canadaRadius;
    #canadaPosition = [225, 75];

    //callbacks
    #callbackClick;
    #callbackHover;
    #callbackZoom;
    #callbackFocus;

    //custom interaction types in highlight
    #clickInteractionType = 'click.highlight';
    #mouseoverInteractionType = 'mouseover';
    #mouseoutInteractionType = 'mouseout';


    //formatters
    #tooltipFunction;

    //Accessibility
    #figureAriaLabel = "Map of Canada";
    #figureAriaDescription = 'Contains different regions within Canada. Press the "Enter" key to tab through the regions. To exit the map, either tab through all the regions or press the "Escape" key';

    //legend
    #legendIntervals;
    #legendValues;
    #legendRectangleWidth = 100;
    #legendRectangleWidthReduction = 15;
    #legendRectangleHeight = 16;
    #legendSpacing = [15, 22];
    #legendPosition = [650, 60];
    #legendTitleHeight = 50;
    #legendTitleWidth = 300;
    #legendTitleX = 0;
    #legendTitle = "Legend title";
    #decimalPlaces = 0;
    #suppressedText = "Suppressed"
    #suppressedLabel = 'suppr.'
    #notApplicableText = "Not available"
    #notApplicableLabel = 'n/a';

    #customLegendTextSeries;

    //map
    #xMap = -500;
    #yMap = 800;
    #mapScale = 0.00015;
    #projection;
    #path;

    #currentZoomScale;
    #currentZoomTransform;



    #transitionDuration = 1000;

    #mapData; //to draw the map
    #data; //to add values to map
    #markerData;

    #markerRadius = 10;
    #markerOpacity = 0.5;
    #markerColour = 'black';
    #markerZoomScaler = 0.5;
    
    


    #width = 900;
    #height = 700;
    #colourSeries = ["#0868ac", "#43a2ca", "#7bccc4", "#bae4bc", "#f0f9e8", "#D3D3D3", 'white'];
    #defaultColour = "#43a2ca";
    #borderColour = "gray";
    #borderHighlightColour = 'black';
    #borderWidth = 1;
    #borderHighlightWidth = 2;

    //region values
    #minRadius = 20;
    #fontSize = 15;
    #offsetNB = [0, 55] //NB
    #offsetNS = [55, 20] //NS
    #offsetPEI = [65, -15] //PEI

    //lookups
    #provinceLookupByAbbr = {
        "QC": "Quebec",
        "NL": "Newfoundland and Labrador",
        "BC": "British Columbia",
        "NU": "Nunavut",
        "NT": "Northwest Territories",
        "NB": "New Brunswick",
        "NS": "Nova Scotia",
        "SK": "Saskatchewan",
        "AB": "Alberta",
        "PE": "Prince Edward Island",
        "YT": "Yukon",
        "MB": "Manitoba",
        "ON": "Ontario"
    };
    #provinceLookupByPRUID = {
        "24": "QC",
        "10": "NL",
        "59": "BC",
        "62": "NU",
        "61": "NT",
        "13": "NB",
        "12": "NS",
        "47": "SK",
        "48": "AB",
        "11": "PE",
        "60": "YT",
        "46": "MB",
        "35": "ON"
    };

    //region Chain methods
    wrapper(input) {
        if (arguments.length === 0) {
            return this.#wrapper;
        }
        else {
            this.#wrapper = input
            return this;
        }
    }
    container(input) {
        if (arguments.length === 0) {
            return this.#container;
        }
        else {
            this.#container = input
            return this;
        }
    }
    regionId(input) {
        if (arguments.length === 0) {
            return this.#regionId;
        }
        else {
            this.#regionId = input
            return this;
        }
    }
    regionName(input) {
        if (arguments.length === 0) {
            return this.#regionName;
        }
        else {
            this.#regionName = input
            return this;
        }
    }
    markerRegionId(input) {
        if (arguments.length === 0) {
            return this.#markerRegionId;
        }
        else {
            this.#markerRegionId = input
            return this;
        }
    }
    xMap(input) {
        if (arguments.length === 0) {
            return this.#xMap;
        }
        else {
            this.#xMap = input
            return this;
        }
    }
    yMap(input) {
        if (arguments.length === 0) {
            return this.#yMap;
        }
        else {
            this.#yMap = input
            return this;
        }
    }
    mapScale(input) {
        if (arguments.length === 0) {
            return this.#mapScale;
        }
        else {
            this.#mapScale = input
            return this;
        }
    }
    projection(input) {
        if (arguments.length === 0) {
            return this.#projection;
        }
        else {
            this.#projection = input
            return this;
        }
    }
    path(input) {
        if (arguments.length === 0) {
            return this.#path;
        }
        else {
            this.#path = input
            return this;
        }
    }
    mapData(input) {
        if (arguments.length === 0) {
            return this.#mapData;
        }
        else {
            this.#mapData = input
            return this;
        }
    }
    data(input) {
        if (arguments.length === 0) {
            return this.#data;
        }
        else {
            this.#data = input
            return this;
        }
    }
    markerData(input) {
        if (arguments.length === 0) {
            return this.#markerData;
        }
        else {
            this.#markerData = input
            return this;
        }
    }
    markerRadius(input) {
        if (arguments.length === 0) {
            return this.#markerRadius;
        }
        else {
            this.#markerRadius = input
            return this;
        }
    }
    markerOpacity(input) {
        if (arguments.length === 0) {
            return this.#markerOpacity;
        }
        else {
            this.#markerOpacity = input
            return this;
        }
    }
    markerColour(input) {
        if (arguments.length === 0) {
            return this.#markerColour;
        }
        else {
            this.#markerColour = input
            return this;
        }
    }
    markerZoomScaler(input) {
        if (arguments.length === 0) {
            return this.#markerZoomScaler;
        }
        else {
            this.#markerZoomScaler = input
            return this;
        }
    }
    regionValueOpacity(input) {
        if (arguments.length === 0) {
            return this.#regionValueOpacity;
        }
        else {
            this.#regionValueOpacity = input
            return this;
        }
    }
    width(input) {
        if (arguments.length === 0) {
            return this.#width;
        }
        else {
            this.#width = input
            return this;
        }
    }
    height(input) {
        if (arguments.length === 0) {
            return this.#height;
        }
        else {
            this.#height = input
            return this;
        }
    }
    ptGroup(input) {
        if (arguments.length === 0) {
            return this.#ptGroup;
        }
        else {
            this.#ptGroup = input
            return this;
        }
    }
    legendGroup(input) {
        if (arguments.length === 0) {
            return this.#legendGroup;
        }
        else {
            this.#legendGroup = input
            return this;
        }
    }
    rvGroup(input) {
        if (arguments.length === 0) {
            return this.#rvGroup;
        }
        else {
            this.#rvGroup = input
            return this;
        }
    }
    invisGroup(input) {
        if (arguments.length === 0) {
            return this.#invisGroup;
        }
        else {
            this.#invisGroup = input
            return this;
        }
    }
    canadaGroup(input) {
        if (arguments.length === 0) {
            return this.#canadaGroup;
        }
        else {
            this.#canadaGroup = input
            return this;
        }
    }
    markerGroup(input) {
        if (arguments.length === 0) {
            return this.#markerGroup;
        }
        else {
            this.#markerGroup = input
            return this;
        }
    }
    currentZoomScale(input) {
        if (arguments.length === 0) {
            return this.#currentZoomScale;
        }
        else {
            this.#currentZoomScale = input
            return this;
        }
    }
    currentZoomTransform(input) {
        if (arguments.length === 0) {
            return this.#currentZoomTransform;
        }
        else {
            this.#currentZoomTransform = input
            return this;
        }
    }


    // #currentZoomScale;
    // #currentZoomTransform;

    canadaValue(input) {
        if (arguments.length === 0) {
            return this.#canadaValue;
        }
        else {
            this.#canadaValue = input
            return this;
        }
    }
    canadaRadius(input) {
        if (arguments.length === 0) {
            return this.#canadaRadius;
        }
        else {
            this.#canadaRadius = input
            return this;
        }
    }
    canadaPosition(input) {
        if (arguments.length === 0) {
            return this.#canadaPosition;
        }
        else {
            const nonEmptyArray = (typeof input == typeof []) &&
                (input.length == 2);
            let allInts = true;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && allInts) {
                this.#canadaPosition = input
                return this;
            }
            else {
                console.error('canadaPosition must be an array of 2 numbers, where the array [x, y] represent the x and y position of the canada region value group');
            }
        }
    }
    legendIntervals(input) {
        //expects input = array of 4 int numbers
        //TODO: Allow non-integer numbers, of varying sizes.
        if (arguments.length === 0) {
            return this.#legendIntervals;
        }
        else {
            const nonEmptyArray = (typeof input == typeof [])
            // &&
            //     (input.length == 4);
            let allInts = true;
            let decrementing = true;
            let lastElement;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                    if (lastElement && lastElement < element) {
                        decrementing = false;
                        break;
                    }
                    lastElement = element;
                }
            }

            // Set field
            if (nonEmptyArray && allInts && decrementing) {
                this.#legendIntervals = input
                return this;
            }
            else {
                console.error('legendIntervals must be an array of decrementing integers');
            }
        }
    }
    customLegendTextSeries(input) {
        if (arguments.length === 0) {
            return this.#customLegendTextSeries;
        }
        else {
            this.#customLegendTextSeries = input
            return this;
        }
    }
    colourSeries(inputKeys) {
        /*
        Parameters 
        ----------------
        inputKeys (type: array)
          - An array of string(s) representing key(s) that the data field has currently selected. 
          - This array should indicate some key(s) to use for the numerical axis
        */

        if (arguments.length === 0) {
            return this.#colourSeries;
        }
        else {
            // Check input
            const nonEmptyArray = (typeof inputKeys == typeof []) &&
                (inputKeys.length > 0);
            let validElements = true;

            if (nonEmptyArray) {
                for (let v of inputKeys) {
                    if ((typeof v != typeof 'abc') || !v) {
                        validElements = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && validElements) {
                this.#colourSeries = inputKeys;
                return this;
            }
            else {
                console.error('colourSeries must be an array of non-empty string(s)');
            }
        }
    }
    minRadius(input) {
        if (arguments.length === 0) {
            return this.#minRadius;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input > 0);

            if (validNum) {
                this.#minRadius = input
                return this;
            }
            else {
                console.error('minRadius must be a number greater than 0');
            }
        }
    }
    fontSize(input) {
        if (arguments.length === 0) {
            return this.#fontSize;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input > 0);

            if (validNum) {
                this.#fontSize = input
                return this;
            }
            else {
                console.error('fontSize must be a number greater than 0');
            }
        }
    }
    transitionDuration(input) {
        if (arguments.length === 0) {
            return this.#transitionDuration;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input >= 0);

            if (validNum) {
                this.#transitionDuration = input
                return this;
            }
            else {
                console.error('transitionDuration must be a non-negative number');
            }
        }
    }
    numberFormat(input) {
        if (arguments.length === 0) {
            return this.#numberFormat;
        }
        else {
            this.#numberFormat = input
            return this;
        }
    }
    numberSeperator(input) {
        if (arguments.length === 0) {
            return this.#numberSeperator;
        }
        else {
            this.#numberSeperator = input
            return this;
        }
    }
    legendRectangleWidth(input) {
        if (arguments.length === 0) {
            return this.#legendRectangleWidth;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input > 0);

            if (validNum) {
                this.#legendRectangleWidth = input
                return this;
            }
            else {
                console.error('legendRectangleWidth must be a number greater than 0');
            }
        }
    }
    legendRectangleWidthReduction(input) {
        if (arguments.length === 0) {
            return this.#legendRectangleWidthReduction;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input >= 0);

            if (validNum) {
                this.#legendRectangleWidthReduction = input
                return this;
            }
            else {
                console.error('legendRectangleWidthReduction must be a non-negative number');
            }
        }
    }
    legendRectangleHeight(input) {
        if (arguments.length === 0) {
            return this.#legendRectangleHeight;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input >= 0);

            if (validNum) {
                this.#legendRectangleHeight = input
                return this;
            }
            else {
                console.error('legendRectangleHeight must be a non-negative number');
            }
        }
    }
    legendSpacing(input) {
        if (arguments.length === 0) {
            return this.#legendSpacing;
        }
        else {
            const nonEmptyArray = (typeof input == typeof []) &&
                (input.length == 2);
            let allInts = true;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && allInts) {
                this.#legendSpacing = input
                return this;
            }
            else {
                console.error('legendSpacing must be an array of 2 numbers, where the numbers represent the x and y spacing of the legend rectangles');
            }
        }
    }
    legendPosition(input) {
        if (arguments.length === 0) {
            return this.#legendPosition;
        }
        else {
            const nonEmptyArray = (typeof input == typeof []) &&
                (input.length == 2);
            let allInts = true;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && allInts) {
                this.#legendPosition = input
                return this;
            }
            else {
                console.error('legendPosition must be an array of 2 numbers, where the numbers represent the x and y translation of the legend group');
            }
        }
    }
    legendTitleHeight(input) {
        if (arguments.length === 0) {
            return this.#legendTitleHeight;
        }
        else {
            const validNum = (typeof input == typeof 5);

            if (validNum) {
                this.#legendTitleHeight = input
                return this;
            }
            else {
                console.error('legendTitleHeight must be a number');
            }
        }
    }
    legendTitleWidth(input) {
        if (arguments.length === 0) {
            return this.#legendTitleWidth;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input > 0);

            if (validNum) {
                this.#legendTitleWidth = input
                return this;
            }
            else {
                console.error('legendTitleWidth must be a number greater than 0');
            }
        }
    }
    legendTitleX(input) {
        if (arguments.length === 0) {
            return this.#legendTitleX;
        }
        else {
            const validNum = (typeof input == typeof 5);

            if (validNum) {
                this.#legendTitleX = input
                return this;
            }
            else {
                console.error('legendTitleX must be a number');
            }
        }
    }
    legendTitle(input) {
        if (arguments.length === 0) {
            return this.#legendTitle;
        }
        else {
            const validString = (typeof input == typeof 'abc') && input;

            if (validString) {
                this.#legendTitle = input
                return this;
            }
            else {
                console.error('legendTitle must be a non-empty string');
            }
        }
    }
    decimalPlaces(input) {
        if (arguments.length === 0) {
            return this.#decimalPlaces;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input >= 0);

            if (validNum) {
                this.#decimalPlaces = parseInt(input)
                return this;
            }
            else {
                console.error('decimalPlaces must be an integer number greater or equal to 0');
            }
        }
    }
    offsetNB(input) {
        if (arguments.length === 0) {
            return this.#offsetNB;
        }
        else {
            const nonEmptyArray = (typeof input == typeof []) &&
                (input.length == 2);
            let allInts = true;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && allInts) {
                this.#offsetNB = input
                return this;
            }
            else {
                console.error('offsetNB must be an array of 2 numbers, where the array [x, y] represent the x and y offset of the value circle from the New Brunswick group');
            }
        }
    }
    offsetNS(input) {
        if (arguments.length === 0) {
            return this.#offsetNS;
        }
        else {
            const nonEmptyArray = (typeof input == typeof []) &&
                (input.length == 2);
            let allInts = true;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && allInts) {
                this.#offsetNS = input
                return this;
            }
            else {
                console.error('offsetNB must be an array of 2 numbers, where the array [x, y] represent the x and y offset of the value circle from the New Brunswick group');
            }
        }
    }
    offsetPEI(input) {
        if (arguments.length === 0) {
            return this.#offsetPEI;
        }
        else {
            const nonEmptyArray = (typeof input == typeof []) &&
                (input.length == 2);
            let allInts = true;

            if (nonEmptyArray) {
                for (let element of input) {
                    if (typeof element != typeof 5) {
                        allInts = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && allInts) {
                this.#offsetPEI = input
                return this;
            }
            else {
                console.error('offsetNB must be an array of 2 numbers, where the array [x, y] represent the x and y offset of the value circle from the New Brunswick group');
            }
        }
    }
    defaultColour(input) {
        if (arguments.length === 0) {
            return this.#defaultColour;
        }
        else {
            this.#defaultColour = input
            return this;
        }
    }
    borderColour(input) {
        if (arguments.length === 0) {
            return this.#borderColour;
        }
        else {
            this.#borderColour = input
            return this;
        }
    }
    borderHighlightColour(input) {
        if (arguments.length === 0) {
            return this.#borderHighlightColour;
        }
        else {
            this.#borderHighlightColour = input
            return this;
        }
    }
    borderWidth(input) {
        if (arguments.length === 0) {
            return this.#borderWidth;
        }
        else {
            this.#borderWidth = input
            return this;
        }
    }
    borderHighlightWidth(input) {
        if (arguments.length === 0) {
            return this.#borderHighlightWidth;
        }
        else {
            this.#borderHighlightWidth = input
            return this;
        }
    }

    figureAriaLabel(input) {
        if (arguments.length === 0) {
            return this.#figureAriaLabel;
        }
        else {
            const validString = (typeof input == typeof 'abc') && input;

            if (validString) {
                this.#figureAriaLabel = input
                return this;
            }
            else {
                console.error('figureAriaLabel must be a non-empty string');
            }
        }
    }

    figureAriaDescription(input) {
        if (arguments.length === 0) {
            return this.#figureAriaDescription;
        }
        else {
            const validString = (typeof input == typeof 'abc') && input;

            if (validString) {
                this.#figureAriaDescription = input
                return this;
            }
            else {
                console.error('figureAriaDescription must be a non-empty string');
            }
        }
    }

    callbackClick(input) {
        if (arguments.length === 0) {
            return this.#callbackClick;
        }
        else {
            this.#callbackClick = input
            return this;
        }
    }
    callbackHover(input) {
        if (arguments.length === 0) {
            return this.#callbackHover;
        }
        else {
            this.#callbackHover = input
            return this;
        }
    }
    callbackZoom(input) {
        if (arguments.length === 0) {
            return this.#callbackZoom;
        }
        else {
            this.#callbackZoom = input
            return this;
        }
    }
    callbackFocus(input) {
        if (arguments.length === 0) {
            return this.#callbackFocus;
        }
        else {
            this.#callbackFocus = input
            return this;
        }
    }

    clickInteractionType(input) {
        if (arguments.length === 0) {
            return this.#clickInteractionType;
        }
        else {
            this.#clickInteractionType = input;
            return this;
        }
    }
    mouseoverInteractionType(input) {
        if (arguments.length === 0) {
            return this.#mouseoverInteractionType;
        }
        else {
            this.#mouseoverInteractionType = input;
            return this;
        }
    }
    mouseoutInteractionType(input) {
        if (arguments.length === 0) {
            return this.#mouseoutInteractionType;
        }
        else {
            this.#mouseoutInteractionType = input;
            return this;
        }
    }

    //formatters
    tooltipFunction(input) {
        if (arguments.length === 0) {
            return this.#tooltipFunction;
        }
        else {
            this.#tooltipFunction = input
            return this;
        }
    }

    //Chaining toggle methods
    interactive(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph interactive. False otherwise.
        */
        if (arguments.length === 0) {
            return this.#interactive;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#interactive = input;
                return this;
            }
            else {
                console.error('interactive must be a boolean');
            }
        }
    }
    displayValues(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph display region values. False otherwise.
        */
        if (arguments.length === 0) {
            return this.#displayValues;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#displayValues = input;
                return this;
            }
            else {
                console.error('displayValues must be a boolean');
            }
        }
    }
    tooltips(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph display region values. False otherwise.
        */
        if (arguments.length === 0) {
            return this.#tooltips;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#tooltips = input;
                return this;
            }
            else {
                console.error('tooltips must be a boolean');
            }
        }
    }
    notApplicable(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the legend display the notApplicable.
        */
        if (arguments.length === 0) {
            return this.#notApplicable;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#notApplicable = input;
                return this;
            }
            else {
                console.error('notApplicable must be a boolean');
            }
        }
    }
    suppressed(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the legend display the suppressed.
        */
        if (arguments.length === 0) {
            return this.#suppressed;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#suppressed = input;
                return this;
            }
            else {
                console.error('suppressed must be a boolean');
            }
        }
    }
    percent(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph display region values. False otherwise.
        */
        if (arguments.length === 0) {
            return this.#percent;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#percent = input;
                return this;
            }
            else {
                console.error('percent must be a boolean');
            }
        }
    }
    canadaBubble(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph display region values. False otherwise.
        */
        if (arguments.length === 0) {
            return this.#canadaBubble;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#canadaBubble = input;
                return this;
            }
            else {
                console.error('canadaBubble must be a boolean');
            }
        }
    }
    zoomable(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph zoomable.
        */
        if (arguments.length === 0) {
            return this.#zoomable;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#zoomable = input;
                return this;
            }
            else {
                console.error('zoomable must be a boolean');
            }
        }
    }
    SINotation(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph zoomable.
        */
        if (arguments.length === 0) {
            return this.#SINotation;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#SINotation = input;
                return this;
            }
            else {
                console.error('SINotation must be a boolean');
            }
        }
    }
    legendGradient(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph zoomable.
        */
        if (arguments.length === 0) {
            return this.#legendGradient;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#legendGradient = input;
                return this;
            }
            else {
                console.error('legendGradient must be a boolean');
            }
        }
    }
    autoTabClick(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the map act like it was clicked instantly on tabbing.
        */
        if (arguments.length === 0) {
            return this.#autoTabClick;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#autoTabClick = input;
                return this;
            }
            else {
                console.error('autoTabClick must be a boolean');
            }
        }
    }
    recalculateLegendIntervals(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to recalculate the legend intervals based on data everytime, this will overwrite manually set legendIntervals though.
        */
        if (arguments.length === 0) {
            return this.#recalculateLegendIntervals;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#recalculateLegendIntervals = input;
                return this;
            }
            else {
                console.error('recalculateLegendIntervals must be a boolean');
            }
        }
    }
    hasRendered(input) {
        if (arguments.length === 0) {
            return this.#hasRendered;
        }
        else {
            this.#hasRendered = input
            return this;
        }
    }
    //endregion

    //region PUBLIC
    init() {
        this.#initProjection();
        this.#initPath();
        this.#initNumberFormat();

        this.#initContainer();
        this.#initPtGroup(); // bottom layer
        this.#initRvGroup();
        this.#initMarkerGroup();
        this.#initCanadaGroup();
        this.#initInvisGroup(); //interactive layer

        return this;
    }

    render() {
        if (this.#data) {
            this.#renderLegend();
        }
        this.#renderMap();
        if (this.#data) {
            this.#renderRegionValues();
        }
        if (this.#markerData) {
            this.#renderMarkers();
        }
        if (this.#canadaBubble) {
            this.#renderCanadaBubble()
        }
        this.#renderInvisMap();

        if (this.#markerData) {
            this.#renderMarkers(this.#invisGroup, true)
        }

        this.#setTabbing(this.#container);
        if (this.#zoomable)
            this.#zoom();

        this.#hasRendered = true;

        return this;
    }

    updateValues(newData) {
        const that = this;
        const mapScale = this.#mapScale;
        const data = this.#data;
        this.#data = newData;
        const minRadius = this.#minRadius;

        const regionId = this.#regionId;

        //#region updateLegend
        if (this.#data) {
            this.#renderLegend();
        }
        //#endregion

        //#region updateRegionValues
        this.#container.selectAll(".region")
            .transition()
            .duration(this.#transitionDuration)
            .style("fill", d => {
                return this.getRegionColour(this.#data[d.properties[regionId]]);
            })

        let regionValues = this.#container.selectAll(".regionValue")
            .transition()
            .duration(this.#transitionDuration)
            .attr('opacity', this.#displayValues ? 1 : 0)

        let circles = regionValues
            .selectAll("circle")
            .transition()
            .duration(this.#transitionDuration)
            .attr('r', (d) => {
                let textVal = this.#getDisplayValue(newData, d)
                let newRadius = this.#calculateRadius(textVal.length, this.#fontSize)
                return newRadius < minRadius ? minRadius : newRadius;
            })


        let text = regionValues
            .selectAll('text')
            .transition()
            .duration(this.#transitionDuration)
            .tween("text", function(d) {
                var selection = d3.select(this);
                var oldVal = parseFloat(selection.text().replaceAll('%', '').replaceAll(that.#numberSeperator, ''));
                let newVal = that.#round(newData[d.properties[regionId]])

                if (!isNaN(oldVal) && !isNaN(newVal)) {
                    const i = d3.interpolate(oldVal, newVal);
                    return function(t) {
                        if (newVal % 1 == 0)
                            selection.text(that.#formatNumber(Math.round(i(t)), d));
                        else
                            selection.text(that.#formatNumber(that.#round(i(t)), d));
                    };
                }
                else {
                    selection
                        .attr('opacity', 0)
                        .text(that.#getDisplayValue(newData, d))
                    selection
                        .transition()
                        .duration(that.#transitionDuration)
                        .attr('opacity', 1)
                }
            })
        //#endregion

        //#region updateCanadaValue
        if (this.#canadaBubble) {
            let canadaValue = this.#calculateCanadaValue();
            //configure the display text
            let textVal = this.#formatNumber(canadaValue)

            let canadaCircle = this.#canadaGroup.select("circle.canadaCircle")
            let canadaCircleText = this.#canadaGroup.select("text.canadaCircleText")
                .transition()
                .duration(this.#transitionDuration)
                .tween("text", function(d) {
                    var selection = d3.select(this);
                    let preParse = selection.text().replaceAll('%', '').replaceAll(that.#numberSeperator, '').replaceAll("−", "-")
                    // console.log("preParse", preParse)
                    var oldVal = parseFloat(preParse);
                    // console.log(oldVal, parseFloat("-9"), parseFloat("−9"))
                    let newVal = canadaValue
                    if (!isNaN(oldVal) && !isNaN(newVal)) {
                        const i = d3.interpolate(oldVal, newVal);
                        return function(t) {
                            if (newVal % 1 == 0)
                                selection.text(that.#formatNumber(Math.round(i(t))));
                            else
                                selection.text(that.#formatNumber(that.#round(i(t))));
                        };
                    }
                    else {
                        // console.log('NaN', oldVal, newVal)
                        selection.text(newVal)
                    }
                })
            // console.log('canadaTextValUpdate', textVal)
            let canadaRadius = this.#calculateCanadaRadius(canadaCircleText, textVal)

            canadaCircle
                .transition()
                .duration(this.#transitionDuration)
                .attr("r", canadaRadius)

            //shift 'Canada' text to accomodate the radius
            this.#canadaGroup.select("text.canadaText")
                .transition()
                .duration(this.#transitionDuration)
                .attr("transform", `translate(${-(canadaRadius + 10)}, 0)`)

        }
        //#endregion

        //#region updateMarkers
        if (this.#markerData) {
            this.#renderMarkers();
            this.#renderMarkers(this.#invisGroup, true)
        }
        //#endregion
        return this;
    }

    magic() {
        this.init()

        this.#hasRendered ? this.updateValues(this.#data) : this.render()

        return this
    }
    //endregion

    //region PRIVATE
    #parseNumber(value) {

    }
    #formatNumber(num, d) {
        if (this.#numberFormat) {
            return this.#numberFormat(num, d)
        }
        return this.#defaultNumberFormat(this.#round(num)).replaceAll(',', this.#numberSeperator) + (this.#percent ? '%' : '')
    }
    #getDisplayValue(data, d) {
        if (!this.#data) {
            return "N/A"
        }
        let value = data[d.properties[this.#regionId]];

        if (value == this.#suppressedLabel && this.#suppressed)
            return value;
        else if (isNaN(value)) {
            return this.#notApplicableLabel;
        }
        else {
            return this.#formatNumber(data[d.properties[this.#regionId]], d)
        }
    }
    #initProjection() {
        this.#projection = d3
            .geoIdentity(function(x, y) {
                return [x, -y];
            })
            .reflectY(true)
            .scale(this.#mapScale)
            .translate([this.#xMap, this.#yMap]);
    }
    #initPath() {
        this.#path = d3.geoPath().projection(this.#projection);
    }
    #initContainer() {
        // console.log(this.#container)
        this.#container
            .attr('width', '100%')
            .attr("viewBox", `0 0 ${this.#width} ${this.#height}`)
            .attr("preserveAspectRatio", "xMinYMin meet")
            .attr('aria-label', this.#figureAriaLabel)
            .attr('aria-description', this.#figureAriaDescription)
            .attr('tabindex', 0)
    }
    #initPtGroup() {
        //create container for pt paths
        this.#ptGroup = this.#container.append('g')
            .attr('class', 'ptGroup')
    }
    #initRvGroup() {
        //create container for region value annotation over the map
        this.#rvGroup = this.#container.append('g')
            .attr('class', 'rvGroup')
    }
    #initMarkerGroup() {
        this.#markerGroup = this.#container.append('g')
            .attr('class', 'markerGroup')
    }
    #initInvisGroup() {
        //create invisible interaction layer that will overlay the map
        this.#invisGroup = this.#container.append('g')
            .attr('class', 'invisGroup')
        // .attr('tabindex', 0)
    }
    #initCanadaGroup() {
        this.#canadaGroup = this.#container
            .append("g")
            .attr("class", "canadaGroup")
    }
    #initNumberFormat() {
        if (this.#SINotation) {
            this.#numberFormat = number => {
                // console.log(d3.formatPrefix(".2s", 1e-2)(number))

                return d3.format(`.2s`)(number).replace('G', 'B');
            }

        }
    }

    getRegionColour(value) {
        const legendValues = this.#legendValues;

        if (!isNaN(value))
            value = this.#round(value)
        // console.log(value)

        let found = false;
        for (let i = 0; i < legendValues.length && !found; i++) {
            if (isNaN(value)) {
                if (value == this.#suppressedLabel && legendValues[i].value == this.#suppressedText && this.#suppressed) {
                    //suppr.
                    found = true;
                    return legendValues[i].colour;
                }
                else if (value != this.#suppressedLabel && legendValues[i].value == this.#notApplicableText && this.#notApplicable) {
                    //n/a
                    found = true;
                    return legendValues[i].colour;
                }
            }
            else if (value >= legendValues[i].value) {
                found = true;
                if (this.#legendGradient) {
                    return this.#legendGradientScale(value)
                }
                return legendValues[i].colour;
            }
            else {
                if (this.#legendGradientScale) {
                    let minVal = d3.min(this.#legendGradientScale.domain())

                    if (value < minVal) {
                        console.log(value, minVal)
                        return this.#legendGradientScale(minVal)
                    }
                }
            }
        }
    }
    #round(number) {
        let multiplier = Math.pow(10, this.#decimalPlaces)
        return Math.round(number * multiplier) / multiplier
    }
    #renderMap() {
        const mapData = this.#mapData;
        const data = this.#data;
        const path = this.#path;
        const legendValues = this.#legendValues;
        const ptGroup = this.#ptGroup

        const regionId = this.#regionId

        // let fake = {}
        // let fake = "pt,region,cars,houses,pets\n";

        //create map paths for different pt's
        var regionPaths = ptGroup
            .selectAll(".region")
            .data(mapData.features)
            .enter()
            .append("g")
            .attr("class", function(d) {
                return "region";
            })
            .attr("data-id", d => d.properties[regionId])
            // .attr("data-taborder", function(d, i) {
            //     // console.log(d.properties)
            //     return d.properties.TABORDER ? d.properties.TABORDER : i
            // })
            .attr("data-pt", d => d.properties["PRNAME"])
            .attr("tabindex", d => -1)
            // .attr("focusable", "true")
            .attr("fill", (d, i) => {
                if (this.#data) {
                    return this.getRegionColour(this.#data[d.properties[regionId]]);
                }
                else {
                    return this.#defaultColour;
                }

            })
            .attr("opacity", 1)

        // console.log('fakeDataGen', fake)

        regionPaths
            .append("path")
            .attr("d", path)
            .attr('stroke', this.#borderColour)
            .attr('stroke-width', this.#borderWidth)

    }
    #highlightRegion(selection) {
        const that = this;
        const ptGroup = this.#ptGroup;
        // const borderWidth = this.#borderWidth;
        // const borderHighlightWidth = this.#borderHighlightWidth;
        const borderColour = this.#borderColour;
        const borderHighlightColour = this.#borderHighlightColour;

        const callbackClick = this.#callbackClick;
        const callbackHover = this.#callbackHover;
        const callbackFocus = this.#callbackFocus;

        if (this.#clickInteractionType) {
            selection
                .on(this.#clickInteractionType, function(e, d) {
                    let selection = d3.select(this)
                    let dataId = selection.attr('data-id')

                    if (callbackClick) {
                        callbackClick(dataId, d)
                    }
                })
        }
        if (this.#mouseoverInteractionType) {
            selection
                .on(this.#mouseoverInteractionType, function(e, d) {
                    let selection = d3.select(this)
                    let dataId = selection.attr('data-id')

                    let gs = ptGroup.select(`.region[data-id='${dataId}']`).raise()
                    gs.select('path')
                        .attr('stroke-width', that.#calculateRegionBorderWidth(that.#borderHighlightWidth))
                        .attr('stroke', borderHighlightColour)
                        // .attr('stroke', 'purple')
                        .attr('class', 'active')

                    if (callbackHover) {
                        callbackHover(dataId)
                    }
                })
        }
        if (this.#mouseoutInteractionType) {
            selection
                .on(this.#mouseoutInteractionType, function(e, d) {
                    let selection = d3.select(this)
                    let dataId = selection.attr('data-id')

                    ptGroup
                        .selectAll(`.region[data-id='${dataId}']`)
                        .select('path')
                        .attr('stroke-width', that.#calculateRegionBorderWidth(that.#borderWidth))
                        .attr('stroke', borderColour)
                        .attr('class', null)
                })
        }
        if (callbackFocus) {
            selection
                .on('focus.highlightRegion', function(e, d) {
                    let selection = d3.select(this)
                    let dataId = selection.attr('data-id')

                    callbackFocus(dataId)
                })
        }
    }
    #calculateMarkerRadius() {
        if (this.#currentZoomScale) {
            let scaleFraction = this.#currentZoomScale * this.#markerZoomScaler;
            let markerSize = scaleFraction >= 1 ? this.#markerRadius / scaleFraction : this.#markerRadius;
            return markerSize;
        }
        return this.#markerRadius;
    }
    #calculateRegionBorderWidth(borderWidth) {
        if (this.#currentZoomScale) {
            let scaleFraction = 1 / this.#currentZoomScale;
            let calcBorderWidth = borderWidth * scaleFraction;
            return calcBorderWidth;
        }
        return borderWidth;
    }
    #calculateOutlineWidth() {
        let baseStrokeWidth = 5;
        if (this.#currentZoomScale) {
            let scaleFraction = 1 / this.#currentZoomScale;
            let calcOutlineWidth = baseStrokeWidth * scaleFraction;
            return calcOutlineWidth;
        }
        return baseStrokeWidth;
    }
    #zoom() {
        const that = this
        let lastClicked;
        // 1 = no zoom in, larger number more zoom
        let zoomMultiplier = 6;

        this.#container.on('click.zoomContainer', function(e) {
            // console.log('zoomContainer', e.target)
            if (e.target.nodeName === 'path') {
                let targetSelection = d3.select(e.target)
                clicked(e, targetSelection.datum())
            }
            else {
                reset()
            }
        })
        // this.#canadaGroup.on('click.zoomCanada', function() {
        //     reset()
        // })
        let paths = this.#invisGroup.selectAll('path')
        // .on('click.zoomPaths', clicked)

        let zoom = d3.zoom()
            // .extent([
            //     [0, 0],
            //     [this.#width, this.#height]
            // ])
            .scaleExtent([1, 8])
            .translateExtent([
                [0, 0],
                [this.#width, this.#height]
            ])
            .on("zoom", zoomed)

        this.#container.call(zoom);
        this.#container.on("dblclick.zoom", null);


        function reset() {
            // console.log('reset click')
            // paths.transition().style("fill", null);
            that.#container.transition().duration(that.#transitionDuration).call(
                zoom.transform,
                d3.zoomIdentity,
                d3.zoomTransform(that.#container.node()).invert([that.#width / 2, that.#height / 2])
            );
            lastClicked = null;
        }

        function clicked(event, d) {
            if (lastClicked == d.properties[that.#regionId]) {
                reset();
            }
            else {

                // let scrollX = window.scrollX, scrollY = window.scrollY;
                // console.log(scrollY)
                lastClicked = d.properties[that.#regionId];
                const [
                    [x0, y0],
                    [x1, y1]
                ] = that.#path.bounds(d);

                that.#container.transition().duration(that.#transitionDuration).call(
                    zoom.transform,
                    d3.zoomIdentity
                    .translate(that.#width / 2, that.#height / 2)
                    .scale(Math.min(zoomMultiplier, 0.9 / Math.max((x1 - x0) / that.#width, (y1 - y0) / that.#height)))
                    .translate(-(x0 + x1) / 2, -(y0 + y1) / 2),
                    d3.pointer(event, that.#container.node())
                );

                // //add tabbing to the groups. This is blocked in setTabbing by event.stopPropagation(), but needed as it would reset() otherwise.
                // that.#invisGroup.selectAll('g').attr('tabindex', 0);
                // that.#canadaGroup.attr('tabindex', 0)

                // window.scrollTo(scrollX, scrollY);

                // event.stopPropagation();
            }
        }

        function zoomed({ transform }) {
            that.#currentZoomScale = transform.k;
            that.#currentZoomTransform = transform;

            that.#ptGroup.attr("transform", transform);
            that.#rvGroup.attr("transform", transform);
            that.#canadaGroup.attr("transform", transform);
            that.#markerGroup.attr("transform", transform);
            if (that.#markerData) {
                // that.#markerGroup.selectAll('circle').attr('transform', transform) //funky 3d effect

                that.#markerGroup.selectAll('circle.marker')
                    .attr('r', that.#calculateMarkerRadius())

                that.#invisGroup.selectAll('circle')
                    .attr('r', that.#calculateMarkerRadius())
                    .attr('stroke-width', that.#calculateOutlineWidth())

                //CSS NEEDED FOR MARKERS OUTLINE ON FOCUS (aka tabbing through)
                // .marker:focus {
                //     outline: none;
                //     opacity: 1;
                // }

                that.#invisGroup.selectAll('circle')
            }
            that.#ptGroup.selectAll('path')
                .attr('stroke-width', function(d) {
                    if (d3.select(this).classed('active')) {
                        return that.#calculateRegionBorderWidth(that.#borderHighlightWidth)
                    }
                    else {
                        return that.#calculateRegionBorderWidth(that.#borderWidth)
                    }
                })

            if (that.#callbackZoom) {
                that.#callbackZoom();
            }
            that.#invisGroup.attr("transform", transform);
        }

    }
    #setTabbing(selection) {
        const that = this;
        const invisGroup = this.#invisGroup;
        const container = this.#container;
        const canadaGroup = this.#canadaGroup;

        selection
            .on('keydown', function(e) {
                const isContainer = e.target.id == container.attr('id');
                const targetSelection = d3.select(e.target)
                // const currSelection = isContainer ? invisGroup : e.target


                if (e.key == 'Enter') {
                    //begin inner tabbing between regions
                    if (isContainer) {
                        let children = invisGroup.selectAll('g.region')
                        if (!children.empty()) {
                            children
                                .attr('tabindex', 0);

                            if (that.#canadaBubble) {
                                canadaGroup.attr('tabindex', 0);
                                // children
                                canadaGroup
                                    ._groups[0][0].focus(); //first child
                                if (that.#autoTabClick) {
                                    d3.select(canadaGroup._groups[0][0]).dispatch('click');
                                }
                            }
                            else {
                                children._groups[0][0].focus(); //first child
                                if (that.#autoTabClick) {
                                    d3.select(children._groups[0][0]).select('path').dispatch('click');
                                }
                            }

                        }
                    }
                    // //enter on a region
                    else if (targetSelection.attr('class') == 'region') {

                        if (!that.#autoTabClick) {
                            // console.log('enter, should be a click', targetSelection.select('path'))
                            targetSelection.dispatch('click');
                        }

                        //if it contains a marker, select it
                        if (that.#markerData) {
                            let markers = targetSelection.selectAll('.marker')
                            markers.attr('tabindex', 0)

                            markers._groups[0][0].focus();
                        }

                    }

                }
                //get out of inner indexes, reset to svg, zoom out
                else if (e.key == 'Escape' && !isContainer) {
                    invisGroup.selectAll('g').attr('tabindex', -1);
                    invisGroup.selectAll('.marker').attr('tabindex', -1);
                    canadaGroup.attr('tabindex', -1);
                    container._groups[0][0].focus();
                    container.dispatch('click')
                }

                //check where in dom. If leaving regions, hide indexes from order. If staying in, zoom
                else if (e.key == "Tab") {
                    let targetSelection = d3.select(e.target);
                    let isMarker = targetSelection.attr('class') == 'marker'
                    let regions = invisGroup.selectAll('g')
                    let allMarkers = invisGroup.selectAll('.marker')
                    let subMarkers = isMarker ?
                        d3.select(e.target.parentNode).selectAll('.marker') :
                        targetSelection.selectAll('.marker');
                    let regionArr = Array.from(regions._groups[0])
                    let markerArr = Array.from(allMarkers._groups[0])
                    let subMarkerArr = Array.from(subMarkers._groups[0])
                    if (that.#canadaBubble) {
                        regionArr.unshift(canadaGroup.node())
                    }
                    let index = regionArr.indexOf(e.target);
                    let markerIndex = markerArr.indexOf(e.target);
                    let subMarkerIndex = subMarkerArr.indexOf(e.target);

                    //if currently on a region, hide markers
                    if (index != -1) {
                        allMarkers.attr('tabindex', -1)
                    }


                    //if at end of subMarkers and you are about to leave, find the next region
                    //forwards leave
                    if (!e.shiftKey && subMarkerIndex != -1 && subMarkerIndex == subMarkerArr.length - 1) {

                        let parentIndex = regionArr.indexOf(e.target.parentNode);
                        //if next group exists, zoom to it
                        if (parentIndex + 1 < regionArr.length && that.#autoTabClick) {
                            d3.select(regionArr[parentIndex + 1]).select('path').dispatch('click')
                        }
                        //else you left the container
                        else {
                            regions.attr('tabindex', -1)
                            allMarkers.attr('tabindex', -1)
                            canadaGroup.attr('tabindex', -1)
                            container.dispatch('click')
                        }
                    }

                    //backwards leave
                    else if (e.shiftKey && subMarkerIndex == 0) {
                        let parentIndex = regionArr.indexOf(e.target.parentNode);
                    }

                    //checks for leaving the container
                    else if (
                        !e.shiftKey &&
                        (
                            (index != -1 && index == regionArr.length - 1) ||
                            (markerIndex != -1 && markerIndex == markerArr.length - 1)
                        )
                    ) {
                        regions.attr('tabindex', -1)
                        allMarkers.attr('tabindex', -1)
                        canadaGroup.attr('tabindex', -1)
                        container.dispatch('click')

                    }
                    else if (e.shiftKey && ((index != -1 && index == 0) || (markerIndex != -1 && markerIndex == 0))) {
                        regions.attr('tabindex', -1)
                        canadaGroup.attr('tabindex', -1)
                        container.dispatch('click')

                    }

                    //checks to zoom into the next tab object
                    if (!e.shiftKey && regionArr[index + 1] && index != -1) {
                        allMarkers.attr('tabindex', -1)
                        if (that.#autoTabClick) {
                            console.log('dispatch click tab')
                            d3.select(regionArr[index + 1]).select('path').dispatch('click')
                        }
                    }
                    else if (e.shiftKey && regionArr[index - 1] && that.#autoTabClick) {

                        let path = d3.select(regionArr[index - 1]).select('path');
                        if (path.empty()) {
                            //if no path, either going back to the canada bubble or the container
                            if (that.#canadaBubble) {
                                d3.select(regionArr[index - 1]).dispatch('click')
                            }
                            else {
                                container.dispatch('click')
                            }
                        }
                        else {
                            //zoom in to the next path that the tab goes to

                            path.dispatch('click')
                        }
                    }
                }
            })
            .on('click.tab', function(e) {
                // console.log(e)
                const isContainer = e.target.id == container.attr('id');

                if (isContainer) {
                    invisGroup.selectAll('g').attr('tabindex', -1);
                    canadaGroup.attr('tabindex', -1)
                }
                else {
                    invisGroup.selectAll('g').attr('tabindex', 0);
                    if (that.#canadaBubble) {
                        canadaGroup.attr('tabindex', 0)
                    }
                }
            })
            .on('focusout', function(e) {

                let regions = invisGroup.selectAll('g')
                let regionArr = Array.from(regions._groups[0])
                let allMarkers = invisGroup.selectAll('.marker')
                let markerArr = Array.from(allMarkers._groups[0])
                if (that.#canadaBubble) {
                    regionArr.unshift(canadaGroup.node())
                }

                if (!regionArr.includes(e.relatedTarget) && !markerArr.includes(e.relatedTarget)) {
                    invisGroup.selectAll('g').attr('tabindex', -1)
                    canadaGroup.attr('tabindex', -1)
                }
            })
    }
    #renderTooltips(selection) {
        const regionId = this.#regionId;
        const regionName = this.#regionName;
        const data = this.#data;

        // console.log('tooltipSelection', selection)

        const tooltip = this.#wrapper.select(".tooltip").empty() ?
            this.#wrapper
            .append('div')
            .attr('class', 'tooltip')
            .attr('opacity', 0) :
            this.#wrapper.select(".tooltip")
        selection
            .on('mouseenter', (e, d) => {
                let html;
                // console.log(e, d, regionId, this.#data)

                let myRegionId;
                // if (typeof d === 'object') {
                myRegionId = this.#data[d.properties[regionId]];
                // } else {
                //     myRegionId = d;
                // }

                let colour = this.#data ? this.getRegionColour(myRegionId) : this.#defaultColour;
                if (this.#tooltipFunction) {
                    html = this.#tooltipFunction(d, colour);
                }
                else {

                    let spanAttr = `style="border-left:5px solid ${colour}; padding-left:3px; display:block"`;
                    html = `<span ${spanAttr}>` + d.properties[regionName] + '<br />';


                    html += `` + this.#getDisplayValue(this.#data, d);
                    html += '</span>';
                }


                tooltip.html(html)
                    .style('opacity', 1)
                    .style("display", "block")
            })
            .on('mouseleave', function(e, d) {
                tooltip
                    .style('opacity', 0)
                    .style("display", "none")
            })
            .on('mousemove', function(e, d) {
                tooltip
                    .style("transform", `translateX(25px)`)
                    .style("left", `${(e.clientX)}px`)
                    .style("top", `${(e.clientY)}px`)
            })
    }
    #renderInvisMap() {
        const that = this;
        const mapData = this.#mapData;
        const path = this.#path;
        const invisGroup = this.#invisGroup;
        const ptGroup = this.#ptGroup;
        const borderWidth = this.#borderWidth;
        const borderColour = this.#borderColour;
        const regionId = this.#regionId;
        const regionName = this.#regionName;
        // console.log('InvisMapData', mapData)

        var invisPaths = invisGroup
            .selectAll(".region")
            .data(mapData.features)
            .enter()
            .append("g")
            .attr("class", function(d) {
                return "region";
            })
            .attr("data-id", d => d.properties[regionId])
            .attr("data-taborder", function(d, i) {
                // console.log(d.properties)
                return d.properties.TABORDER ? d.properties.TABORDER : i
            })
            .attr("data-pt", d => d.properties["PRNAME"])
            .attr("tabindex", d => -1)
            .attr("focusable", "true")
            .attr("aria-label", d => `${d.properties[regionName]}: ${this.#getDisplayValue(this.#data, d)}`)

        if (this.#interactive) {
            this.#highlightRegion(invisPaths);
        }
        if (this.#tooltips) {
            this.#renderTooltips(invisPaths);
        }

        invisPaths.sort((a, b) => {
            return (+a.properties.TABORDER) - (+b.properties.TABORDER)
        })

        invisPaths
            .append("path")
            .attr("d", path)
            .attr('stroke', this.#borderColour)
            .attr('stroke-width', this.#borderWidth)
            .attr('opacity', 0)
    }
    #renderRegionValues() {
        const mapScale = this.#mapScale;
        const xMap = this.#xMap;
        const yMap = this.#yMap;
        const data = this.#data;
        const mapData = this.#mapData;
        const regionId = this.#regionId;

        // let pt = topojson.feature(mapData, mapData.objects.Can_PR2016);

        const offsetNB = this.#offsetNB;
        const offsetNS = this.#offsetNS;
        const offsetPEI = this.#offsetPEI;

        let regionValues = this.#rvGroup
            .selectAll(".regionValue")
            .data(mapData.features)
            .enter()
            .append("g")
            .attr("class", 'regionValue')
            .attr("data-id", d => d.properties[regionId])
            .attr("data-pt", d => d.properties["PRNAME"])
            .attr("tabindex", d => -1)
            .attr('transform', function(d, i) {
                // get the largest sub-polygon's coordinates
                let coord = d.geometry.coordinates;

                if (d.geometry.type == 'MultiPolygon') {
                    const u = d3.scan(coord.map(function(p) {
                        return -d3.polygonArea(p[0]);
                    }));
                    if (u == undefined) {
                        coord = [coord];
                    }
                    else {
                        coord = coord[u];
                    }
                }
                const n = polylabel(coord, 0.01)
                // if (d.properties[regionId] == 10) {
                //     d3.select(this.parentNode.parentNode).raise();
                // }
                return "translate(" + ((n[0] * (mapScale)) + xMap) + "," + (+n[1] * (-1 * mapScale) + yMap) + ")";
            })
            .attr('opacity', this.#displayValues ? 1 : 0)


        if (this.#interactive) {
            this.#highlightRegion(regionValues);
        }
        if (this.#tooltips) {
            this.#renderTooltips(regionValues);
        }

        let circles = regionValues
            .append("circle")
            .attr("class", "regionValuesCircle")
            .attr("r", d => {
                let textVal = this.#getDisplayValue(this.#data, d)
                let newRadius = this.#calculateRadius(textVal.length, this.#fontSize)
                return newRadius < this.#minRadius ? this.#minRadius : newRadius;
            })
            .attr("fill", "rgb(54, 54, 54)")
            .attr("stroke", "none")

        let text = regionValues
            .append("text")
            .attr('class', "regionValuesText")
            .attr('opacity', 1)
            // .attr("stroke", "white")
            .attr("fill", "white")
            .attr("font-size", `${this.#fontSize}px`)
            .attr('alignment-baseline', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('text-anchor', 'middle')
            .style('user-select', 'none')
            .text((d) => {
                return this.#getDisplayValue(this.#data, d);
            })


        //Tweak positioning and size of text for regions whos circles cannot fit inside. EX: PEI, NB, NS
        regionValues.each(function(d) {
            let selection = d3.select(this);
            const currentTransform = selection.attr('transform')
            const transformVals = currentTransform.substring(currentTransform.indexOf("(") + 1, currentTransform.indexOf(")")).split(/[\s,]+/);

            function applyOffset(offsetInput) {
                selection.attr("transform", "translate(" + ((+transformVals[0]) + (+offsetInput[0])) + "," + ((+transformVals[1]) + (+offsetInput[1])) + ")");

                selection.insert("line", "circle")
                    .attr("class", "regionDeathsLine")
                    .attr("x1", 0)
                    .attr("y1", 0)
                    .attr("x2", -offsetInput[0])
                    .attr("y2", -offsetInput[1])
                    .attr("stroke-width", 2)
                    .attr("stroke", "rgb(54, 54, 54)")
            }

            if (d.properties[regionId] == 13) {
                applyOffset(offsetNB) //Shift the value circle for New Brunswick
            }
            else if (d.properties[regionId] == 12) {
                applyOffset(offsetNS) //Nova Scotia
            }
            else if (d.properties[regionId] == 11) {
                applyOffset(offsetPEI) //Prince Edward Island
            }
        });
    }
    #renderMarkers(markerGroup = this.#markerGroup, invis = false) {
        const that = this;
        // console.log(markerGroup, this.#markerData)
        let myGroup = !invis ? markerGroup : markerGroup.selectAll('g.region');
        myGroup
            .selectAll('circle.marker')
            .data(d => !invis ?
                this.#markerData :
                this.#markerData.filter(md => md.properties[this.#markerRegionId] == d.properties[this.#regionId])
            )
            .join(
                enter => {
                    enter
                        .append('circle')
                        .attr('tabindex', -1)
                        .attr("cx", (d) => {
                            return this.#projection([d.coordinates[0], d.coordinates[1]])[0]; // Put coordinates from the circle here
                        })
                        .attr("cy", (d) => {
                            return this.#projection([d.coordinates[0], d.coordinates[1]])[1]; // And here
                        })
                        .attr('r', (d) => {
                            return this.#calculateMarkerRadius()
                            // return Math.ceil(Math.random() * 20)
                        })
                        .attr('fill', invis ? 'none' : this.#markerColour)
                        .attr('stroke', invis ? 'black' : 'none')
                        .attr('stroke-width', invis ? 2 : 0)
                        .attr('class', 'marker')
                        .attr('opacity', 0)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', invis ? 0 : this.#markerOpacity)
                },
                update => {
                    update
                        .transition()
                        .duration(this.#transitionDuration / 2)
                        .attr('opacity', 0)
                        .on('end', function(d, i) {
                            d3.select(this)
                                .attr("cx", (d) => {
                                    return that.#projection([d.coordinates[0], d.coordinates[1]])[0]; // Put coordinates from the circle here
                                })
                                .attr("cy", (d) => {
                                    return that.#projection([d.coordinates[0], d.coordinates[1]])[1]; // And here
                                })
                                .transition()
                                .duration(that.#transitionDuration / 2)
                                // .attr('r', (d) => {
                                //     return that.#calculateMarkerRadius()
                                // })
                                .attr('opacity', invis ? 0 : that.#markerOpacity)
                        })

                },
                exit => {
                    exit.transition().duration(this.#transitionDuration / 2).attr('opacity', 0).remove()
                }
            )
    }
    #calculateCanadaValue() {
        let canadaValue = this.#canadaValue ?? 0;

        //calculate the canada value by default if one is not provided
        if (!this.#canadaValue) {
            let count = 0;
            for (let regionValue in this.#data) {
                let val = +this.#data[regionValue]
                if (!isNaN(val)) {
                    canadaValue += val;
                    count++;
                }
            }

            if (this.#percent && count !== 0) {
                canadaValue /= count
            }
        }
        else {

        }
        return canadaValue;
    }
    #calculateCanadaRadius(element, value) {
        if (this.#canadaRadius) {
            return this.#canadaRadius;
        }
        let canadaTextFont = parseFloat(window.getComputedStyle(element.node(), null)["fontSize"])
        let padding = this.#SINotation ? 5 : 0
        let newRadius = this.#calculateRadius(value.toString().length, canadaTextFont) + padding
        return newRadius < this.#minRadius ? this.#minRadius : newRadius;
    }
    #renderCanadaBubble() {
        let canadaGroupContainer = this.#canadaGroup.append('g')
            .attr("transform", `translate(${this.#canadaPosition[0]},${this.#canadaPosition[1]})`);

        let canadaValue = this.#calculateCanadaValue();

        let textVal;
        //configure the display text
        if (typeof canadaValue === 'string') {
            textVal = canadaValue;
        }
        else {
            textVal = this.#formatNumber(canadaValue)
        }
        // console.log('canadaTextVal', textVal)

        // let canadaBackground = canadaGroupContainer.append('rect')
        //canadaCircle renders first to get the proper overlap. attributes come later so that we can modify the radius to accomodate the fully rendered text in the circle
        let canadaCircle = canadaGroupContainer.append("circle")
        let canadaCircleText = canadaGroupContainer.append("text")
            .attr('class', "canadaCircleText")
            .attr("fill", "white")
            // .attr("stroke", "white")
            .attr('alignment-baseline', 'middle')
            .attr('text-anchor', 'middle')
            .text(textVal)

        // console.log
        console.log('canadaTextValRender', textVal)
        let canadaRadius = this.#calculateCanadaRadius(canadaCircleText, textVal)

        canadaCircle
            .attr("class", "canadaCircle")
            .attr("r", canadaRadius)
            .attr("fill", "rgb(54, 54, 54)")
            .attr("stroke", "none")

        //shift 'Canada' text to accomodate the radius
        canadaGroupContainer.append("text")
            .attr("class", "canadaText")
            .attr("transform", `translate(${-(canadaRadius + 10)}, 0)`)
            .attr('text-anchor', 'end')
            .attr('alignment-baseline', 'middle')
            // .attr('dominant-baseline', 'middle')
            .text("Canada")

        // let bounding = canadaGroupContainer.node().getBBox();
        // let rectPadding = 5
        // canadaBackground
        //     .attr('opacity', 0.8)
        //     .attr('fill', 'white')
        //     .attr('rx', 10)
        //     .attr('ry', 10)
        //     .attr('x', bounding.x - rectPadding)
        //     .attr('y', -bounding.height / 2 - rectPadding)
        //     .attr('width', bounding.width + rectPadding * 2)
        //     .attr('height', bounding.height + rectPadding * 2)
    }
    #calculateRadius(textLength, textSize) {
        if (textLength == 1)
            return textLength * (textSize / 1.5)
        else if (textLength == 2)
            return textLength * (textSize / 2.5)
        else
            return textLength * (textSize / 3)
    }
    #calculateLegendIntervals() {
        //determining the intervals for the legend values
        let legendIntervals = []
        let maxVal = 0;
        let minVal = 0;
        for (let i in this.#data) {
            if (maxVal < this.#data[i]) {
                maxVal = this.#data[i];
            }
            if (minVal > this.#data[i]) {
                minVal = this.#data[i];
            }
        }

        let topInterval = Math.ceil(maxVal * .75);
        legendIntervals.push(topInterval);
        legendIntervals.push(Math.ceil(topInterval * .75))
        legendIntervals.push(Math.ceil(topInterval * .5))
        legendIntervals.push(Math.ceil(topInterval * .25))
        legendIntervals.push(minVal)

        // console.log("legendIntervals", legendIntervals)

        this.#legendIntervals = legendIntervals;
    }
    #setLegendValues() {
        const legendIntervals = this.#legendIntervals;
        const colourSeries = this.#colourSeries;

        let count = 0;
        this.#legendValues = []
        this.#legendIntervals.map((el, i) => {
            this.#legendValues.push({ "value": legendIntervals[i], "colour": colourSeries[i] })
            count++;
        })

        if (this.#notApplicable) {
            this.#legendValues.push({ "value": this.#notApplicableText, "colour": colourSeries[count++] })
        }
        if (this.#suppressed) {
            this.#legendValues.push({ "value": this.#suppressedText, "colour": colourSeries[count] }, )
        }

        // console.log(this.#legendValues)
    }
    #renderLegend() {
        let language = d3.select('html').attr('lang');

        const colourSeries = this.#colourSeries;
        if (!this.#legendIntervals || this.#recalculateLegendIntervals) {
            this.#calculateLegendIntervals();
        }
        this.#setLegendValues();

        const that = this;

        this.#legendValues;

        const rectWidth = this.#legendRectangleWidth;
        const rectReduction = this.#legendRectangleWidthReduction;
        const rectHeight = this.#legendRectangleHeight;
        const legendSpacing = this.#legendSpacing;
        const legendPosition = this.#legendPosition;
        const titleHeight = this.#legendTitleHeight;
        const titleWidth = this.#legendTitleWidth;
        const titleX = this.#legendTitleX;
        const title = this.#legendTitle;
        const notApplicableText = this.#notApplicableText;
        const suppressedText = this.#suppressedText;

        let joiningWord;
        let moreWord;

        if (language == "fr") {
            joiningWord = 'à';
            moreWord = 'et plus';
        }
        else {
            joiningWord = 'to'
            moreWord = 'and higher'
        }

        function wrap(text, width) {
            text.each(function() {
                var text = d3.select(this),
                    words = text.text().split(/\s+/).reverse(),
                    word,
                    line = [],
                    alignmentBaseline = text.attr('alignment-baseline'),
                    lineNumber = 0,
                    lineHeight = 1.1, // ems
                    x = text.attr("x"),
                    y = text.attr("y"),
                    dy = 0, //parseFloat(text.attr("dy")),
                    tspan = text
                    .text(null)
                    .append("tspan")
                    .attr("x", x)
                    .attr("y", y)
                    .attr('alignment-baseline', alignmentBaseline)
                    .attr("dy", dy + "em");
                while ((word = words.pop())) {
                    line.push(word);
                    tspan.text(line.join(" "));
                    if (tspan.node().getComputedTextLength() > width) {
                        line.pop();
                        tspan.text(line.join(" "));
                        line = [word];
                        tspan = text
                            .append("tspan")
                            .attr("x", x)
                            .attr("y", y)
                            .attr('alignment-baseline', alignmentBaseline)
                            .attr("dy", ++lineNumber * lineHeight + dy + "em")
                            .text(word);
                    }
                }
            });
        }

        //legend for interactive map, check if it already exists for update
        let legend = this.#container.select('g.legend');
        if (legend.empty()) {
            legend = this.#container
                .append("g")
                .attr("class", "legend")
                .attr("transform", `translate(${legendPosition[0]}, ${legendPosition[1]})`)
        }
        this.#legendGroup = legend;

        //background rectangle of legend, check if it exists, remove if it does. add background and lower so its behind always
        let legendBackground = legend.select('rect.background')
        if (!legendBackground.empty()) {
            legendBackground.remove();
        }
        legendBackground = legend.append('rect')
            .attr('class', 'background')
            .lower();

        //legend-title, check if it exists. update text if it does
        let legendTitle = legend.select("text.legend-title")
        if (legendTitle.empty()) {
            legendTitle = legend.append("text")
                .attr("class", "legend-title")
                .attr("y", 0)
                .attr("x", titleX)
                .attr("alignment-baseline", 'hanging')
                .text(title ? title : "")

            wrap(legendTitle, titleWidth)
        }
        else {
            legendTitle
                .attr("y", 0)
                .attr("x", titleX)
                .attr("alignment-baseline", 'hanging')
                .text(title ? title : "")

            wrap(legendTitle, titleWidth)
        }



        //create legend gradient piece for each part of legendValues
        if (this.#legendGradient) {
            legend.selectAll('.legend-group').remove()
            let legendGroup = legend.append("g")
                .attr("class", "legend-group")
                .attr("transform", "translate(0, " + (titleHeight + legendSpacing[1]) + ")")
            let gradientLegendValues = [...this.#legendValues]
            console.log('legendValues', this.#legendValues);
            if (this.#notApplicable) {
                gradientLegendValues.pop();
            }
            if (this.#suppressed) {
                gradientLegendValues.pop();
            }

            let extent = d3.extent(gradientLegendValues, d => d.value);
            // console.log(extent)
            let dataValues = [];
            for (let i in this.#data) {
                if (!isNaN(this.#data[i]))
                    dataValues.push(this.#data[i]);
            }
            let dataMax = d3.max(dataValues);
            // console.log(dataValues)
            extent[1] = extent[1] > dataMax ? extent[1] : dataMax;

            // console.log(extent)

            //A color scale
            this.#legendGradientScale = d3.scaleLinear()
                .domain(this.#legendIntervals.reverse())
                .range(gradientLegendValues.map(el => el.colour).reverse())

            let defs = legendGroup.append("defs");
            let linearGradient = defs.append("linearGradient").attr("id", `${this.#container.attr('id')}-urlGradient`);

            // horizontal gradient
            linearGradient
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "0%");

            linearGradient.selectAll("stop")
                .data(gradientLegendValues)
                .enter().append("stop")
                .attr("offset", (d, i) => {
                    // return ((d.value - extent[1]) / (extent[0] - extent[1]) * 100) + "%"
                    return 100 * (i / (gradientLegendValues.length - 1)) + "%"
                })
                .attr("stop-color", (d, i) => gradientLegendValues[gradientLegendValues.length - 1 - i].colour);

            legendGroup.append("rect")
                .attr("width", rectWidth)
                .attr("height", rectHeight)
                .attr('stroke', 'black')
                .attr("fill", `url(#${this.#container.attr('id')}-urlGradient)`);

            legendGroup.selectAll('text.legendLabel')
                .data(extent)
                .enter().append('text').attr('class', 'legendLabel')
                .attr('text-anchor', (d, i) => i == 0 ? 'start' : 'end')
                .attr('alignment-baseline', 'hanging')
                .attr('x', (d, i) => i == 0 ? 0 : rectWidth)
                .attr('y', (d, i) => rectHeight + 3)
                .text(d => d + (this.#percent ? '%' : ''))
        }
        //legend with buckets
        else {
            legend.selectAll('g.legend-group')
                .data(this.#legendValues)
                .join(
                    enter => {
                        let legendGroup = enter.append("g")
                            .attr("class", "legend-group ")
                            .attr("transform", (d, i) => "translate(0, " + (titleHeight + legendSpacing[1] * i) + ")")

                        legendGroup.append('text')
                            .attr("text-anchor", "end")
                            .text((d, i) => {
                                let str = ""
                                let value = this.#round(d.value)
                                if (this.#customLegendTextSeries && this.#customLegendTextSeries[i]) {
                                    str = this.#customLegendTextSeries[i];
                                }
                                else if (i === 0) {
                                    str = value + (this.#percent ? '%' : '') + ` ${moreWord}`;
                                }
                                else if (d.value === notApplicableText || d.value === suppressedText) {
                                    str = d.value
                                }
                                else {
                                    let v1 = this.#round(this.#legendValues[i-1].value);
                                    let v2 = Math.pow(10, -this.#decimalPlaces);
                                    let calcValue = this.#round(v1 - v2);
                                    if (calcValue <= value){
                                        str = value + (this.#percent ? '%' : '');
                                    } else {
                                        str = `${value + (this.#percent ? '%' : '')} ${joiningWord} ${calcValue + (this.#percent ? '%' : '')}`;
                                    }
                                }
                                return str;
                            });

                        legendGroup.append("rect")
                            .attr("width", (d, i) => rectWidth - rectReduction * i)
                            .attr("height", rectHeight)
                            .attr("fill", (d, i) => d.colour)
                            .attr("stroke", "gray")
                            .attr("x", legendSpacing[0])
                            .attr("y", -rectHeight)
                    },
                    update => {
                        update
                            .transition()
                            .duration(this.#transitionDuration)
                            .attr("transform", (d, i) => "translate(0, " + (titleHeight + legendSpacing[1] * i) + ")")

                        update.select('text')
                            .attr("text-anchor", "end")
                            .text((d, i) => {
                                let str = ""
                                let value = this.#round(d.value)
                                if (this.#customLegendTextSeries && this.#customLegendTextSeries[i]) {
                                    str = this.#customLegendTextSeries[i];
                                }
                                else if (i === 0) {
                                    str = value + (this.#percent ? '%' : '') + ` ${moreWord}`;
                                }
                                else if (d.value === notApplicableText || d.value === suppressedText) {
                                    str = d.value
                                }
                                else {
                                    let v1 = this.#round(this.#legendValues[i-1].value);
                                    let v2 = Math.pow(10, -this.#decimalPlaces);
                                    let calcValue = this.#round(v1 - v2);
                                    if (calcValue <= value){
                                        str = value + (this.#percent ? '%' : '');
                                    } else {
                                        str = `${value + (this.#percent ? '%' : '')} ${joiningWord} ${calcValue + (this.#percent ? '%' : '')}`;
                                    }
                                }
                                return str;
                            });

                        update.select("rect")
                            .transition()
                            .duration(this.#transitionDuration)
                            .attr("width", (d, i) => rectWidth - rectReduction * i)
                            .attr("height", rectHeight)
                            .attr("fill", (d, i) => d.colour)
                            .attr("stroke", "gray")
                            .attr("x", legendSpacing[0])
                            .attr("y", -rectHeight)

                    },
                    exit => {
                        exit.remove()
                    }
                )
        }

        //change background rect position and size to fit text/rect/title
        let bounding = legend.node().getBBox();
        let rectPadding = 10
        legendBackground
            .attr('opacity', 0.8)
            .attr('fill', 'white')
            .attr('rx', 10)
            .attr('ry', 10)
            .attr('x', bounding.x - rectPadding)
            .attr('y', -rectPadding)
            .attr('width', bounding.width + rectPadding * 2)
            .attr('height', bounding.height + rectPadding * 2)
    }

    #getCssProperty(element, property) {
        return window.getComputedStyle(element, null).getPropertyValue(property);
    }
    #getFullFont(element) {
        let fontWeight = this.#getCssProperty(element, 'font-weight') || 'normal';
        let fontSize = this.#getCssProperty(element, 'font-size') || '16px';
        let fontFamily = this.#getCssProperty(element, 'font-family') || '"Noto Sans",sans-serif';
        return `${fontWeight} ${fontSize} ${fontFamily}`;
    }
    #calculateTextDimensions(text, font) {
        let canvas = this.#calculateTextDimensions.canvas || (this.#calculateTextDimensions.canvas = document.createElement("canvas"));
        let context = canvas.getContext("2d");
        context.font = font;
        let metrics = context.measureText(text);
        // console.log('metrics', metrics)
        let width = metrics.width;
        let height = metrics.fontBoundingBoxAscent;
        return { width, height };
    }
    //endregion
}
"""
        documentation = """# Map Class

The aim of this class is to quickly create 
reusable maps of Canada. Your job is to just send 
in the right data and style the graph with built in parameters or custom CSS.

##*Requirements*
 - Topojson library: `https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js`
 - PolyLabel: found internally at `/src/js/polylabel.js`
 - `Can_PR2016`: for Canadian provinces/territories map data `/src/json/Can_PR2016.json`
    - Health Regions data: `/src/json/health-regions-2022.json`


### Quickstart

First, create an `index.html` file and `main.js` 
file. For this example, they are made in the same directory. 
- For the HTML file, ensure 
  you have a div whose only child is an SVG element.
- Also **ensure that you load the `d3.js` library 
  and `main.js` as a module** (in that order).
- Example:

```
(index.html)
--------------------
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Map of Canada</title>
    <link href="./css/dummy.css" rel="stylesheet" type="text/css">
</head>
<body>
<body>
  <div id='mapWrapper'>
    <svg id='map'></svg>
  </div>
</body>

<script src="https://d3js.org/d3.v7.min.js"></script>
<!--for map-->
<script src="/src/js/polylabel.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
<!-- -->
<script src='./main.js' type='module'></script>

</html>
```

Next, import `Map` from `map.js` in `main.js`. 
Can use this code as an example in `main.js` to 
initialise the map.

```
import { Map } from "/src/js/modular/map.js";

const map = new Map();
map
    .wrapper(d3.select('#mapWrapper'))
    .container(d3.select('#map'))
```

Now, add some more code to `main.js` to load the canada map 
data as well as the data you want to display on the map. 
First, the map data using `d3.json`:

```
d3.json(`/src/json/Can_PR2016.json`, (mapData) => mapData)
    .then(mapData => {
        map.mapData(topojson.feature(mapData, mapData.objects.Can_PR2016)); //mapData.objects.Can_PR2016 may be different if using different mapData
        
        //rest of code
    })

```

Note: the *data format for display must be key value pairs*.
 - *key*: PRUID of the province/territory
 - *value*: Value to be displayed for that province/territory
 - Format example: 
 ```
 let keyValue = {
    24:7,
    10:2,
    59:6,
    62:1,
    61:0,
    13:9,
    12:5,
    47:8,
    48:10,
    11:10,
    60:3,
    46:4,
    35:10
}
```
You can process your display data with a conversion
function. You can place the whole `d3.csv()` block within the last `d3.json().then()`
to avoid async issues.
```
function csvToKeyValue(data, keyName, valueName){
    let newData = {};
    for (let i of data){
        newData[i[keyName]] = i[valueName]
    }
    return newData;
}

d3.csv("./data/dummyPT.csv", (data) => data).then(data => {
    
    let formattedData = csvToKeyValue(data, "pt", "value")
    map
        .data(formattedData)
        .init()
        .render();
})
```

This should now create a basic map of Canada.

It is common with maps to want to *update the values*. This 
can be acheived easily by calling and passing in new 
data to `map.updateValues(updateData)`.
The data must be in the same format.

The methods for the map chain, meaning you can call them after one another. 
Methods that simply set an attribute of the map, can be left empty to get 
the value instead. Ex: `map.data(yourData)` sets the data, `map.data()` gets the data.

Here are a list of different ways you can customize all aspects of the map:

Customize the map
 - *Display data*: `map.data(csv)`
    - Not assigning this will create a uniformly coloured map without values or a legend
 - *Map data*: `map.mapData(topojson.feature(mapData, mapData.objects.yourObjectName)`
    - Creates the literal map, must be assigned.
 - *Marker data*: `map.markerData(markerData.objects.yourObjectName.geometries)`
    - Must have coordinates
    - `OUTLINE MARKERS ON TAB: css`
    // .marker:focus {
    //     outline: none;
    //     opacity: 1;
    // }
 - *Horizontal shift*: `map.xMap(-500)`
 - *Vertical shift*: `map.yMap(800)`
 - *Scale*: `map.mapScale(0.00015)`
 - *Viewbox width*: `map.width(900)`
 - *Viewbox height*: `map.height(700)`
 - *Radius of value circles*: `map.minRadius(20)`
 - *Fontsize of value circles*: `map.fontSize(15)`
 - *Value circle offset [x, y]*: 
    - New Brunswick: `map.offsetNB([0, 55])`
    - Nova Scotia: `map.offsetNS([55, 20])`
    - Prince Edward Island: `map.offsetPEI([65, -15])`
 - *Map / Legend colours*: `map.colourSeries(["#0868ac", "#43a2ca", "#7bccc4", "#bae4bc", "#f0f9e8", "#D3D3D3"])`
    - Determines the colours for the legendIntervals --> Not applicable --> Suppressed, in that order (if they are defined)
 - *Default colour*: `map.defaultColour("#43a2ca")`
    - Sets the default colour of the map if no data is given
 - *Border colour*: `map.borderColour("gray")`
 - *Border highlight colour on hover*: `map.borderHighlightColour("black")`
 - *Border width*: `map.borderWidth(1)`
 - *Border highlight width on hover*: `map.borderHighlightWidth(2)`
 - *Decimal roundoff*: `map.decimalPlaces(0)`;
 - *Number seperator (thousands)*: `map.numberSeperator(" ")`;

Toggle Options
 - *Interactive*: `map.interactive(true)`
    - Turns hover and click options on/off.
 - *displayValues*: `map.displayValues(true)`
    - Displays the region value for each region
 - *Tooltips*: `map.tooltips(true)`
 - *Suppressed*: `map.suppressed(true)`
    - Add suppressed option to the legend.
 - *notApplicable*: `map.notApplicable(true)`
    - Add n/a option to the legend
 - *percent*: `map.percent(true)`
    - Displays the legend and region values as percents
 - *canadaBubble*: `map.canadaBubble(true)`
    - Displays a canada region value in the top left by default
    - To manually change the value, use `map.canadaValue(yourValue)` where *yourValue* is a number
 - *Zoomable*: `map.zoomable(true)`
    - Adds zoom, drag, click focus, zoom on tab, scroll wheel
 - *Scientific Notation*: `map.SINotation(true)`


Callback functions (requires interactive to be true). Executes the callback function when condition is met
 - *Callback on click*: `map.callbackClick(yourCallbackFunction)`
 - *Callback on hover*: `map.callbackHover(yourCallbackFunction)`

Region identifiers (changes based on mapData set)
 - *Region ID*: `map.regionId("PRUID")`
 - *Region name*: `map.regionName("PRENAME")`

Accessibility
 - *figureAriaLabel*: `map.figureAriaLabel("Map of Canada")`;
 - *figureAriaDescription*: `map.figureAriaDescription('Map description, can be used to show users how to get in. The default description does this generically')`;

Customize the legend
 - *Colour intervals*: `map.legendIntervals([1000, 100, 50, 10, 0])`
 - *Rectangle width*: `map.legendRectangleWidth(100)`
 - *Rectangle width reduction value*: `map.legendRectangleWidthReduction(15)`
 - *Rectangle height*: `map.legendRectangleHeight(16)`
 - *Spacing between legend elements [x, y]*: `map.legendSpacing([15, 22])`
    - x: distance between text and rectangle
    - y: distance between vertical rect/text groups
 - *Position [x,y]*: `map.legendPosition([650, 60])`
 - *Title height*: `map.legendTitleHeight(50)`
 - *Title width*: `map.legendTitleWidth(300)`
    - Will wrap the title if it extends beyond the declared width
 - *Horizontal title translation*: `map.legendTitleX(0)`
 - *Title text*: `map.legendTitle("Legend title")`
 - *Suppressed*: `map.suppressed(true)`
    - Add suppressed option to the legend.
 - *notApplicable*: `map.notApplicable(true)`
    - Add n/a option to the legend
 - *Suppressed text*: `suppressedText("Suppressed")`
    - How it shows in legend
 - *Suppressed label*: `suppressedLabel("suppr.")`
    - How it shows in region values
 - *Not applicable text*: `notApplicableText("Not available")`
    - Display in legend
 - *Not applicable label*: `notApplicableLabel("n/a")`
    - Display in region values

Selections:
 - *Wrapper div*: `map.wrapper(selection)`
 - *Container svg*: `map.container(selection)`

`OVERWRITE AT YOUR OWN RISK. will probably break everything :). Use to get selection groups as demonstrated if needed`
 - *Region group (visible)*: `map.ptGroup()`
 - *Region values overlaid over regions*: `map.rvGroup()`
 - *Interactive layer*: `map.invisGroup()`
 - *Legend*: `map.legend()`
 - *Canada group and value*: `map.canadaGroup()`
 - *Markers overlaid over regions*: `map.markerGroup()`
    """
    elif graph_type == 'pie':
        source = """export class PieChart {
    #data;
    #cKey;
    #cValues;
    #nKey;

    #wrapper;
    #container;
    #pieGroup;
    #invisPieGroup;

    #table;
    #tableCaption;
    #tableSummary = d3.select('html').attr('lang') == "fr" ? "Texte descriptif" : "Text description";
    #tableHeaderFunction;
    #tableCellFunction;
    #figureAriaLabel = "Pie chart";
    #figureAriaDescription = '';

    //add labels, add legend, add interaction, in that order

    #width = 720;
    #height = 480;
    #margins = { l: 100, r: 60, t: 60, b: 100 };
    #graphPosition;

    //pie values
    #pie;
    #radius = Math.min(this.#width, this.#height) / 2 * 0.9;
    #inner;
    #outer;
    #arc;
    #outerArc;

    #legendGroup;
    #legendRadius = 8;
    #legendTextOffset = 15;
    #legendCircleSpacing = 28;
    #legendSpacingFromGraph = 20;
    #legendOrientation = 'v';
    #legendPosition;

    #decimalPlaces
    #decimalType = "round";


    #colourSeries = ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#37A86F", "#edc949", "#af7aa1", "#ff9da7", "#9c755f", "#bab0ab"];
    #colourScale;

    #graphTitle;

    #transitionDuration = 1000;

    #hasRendered = false;

    #captionAbove = false;
    #isDataTable = true;
    #tooltips = false;

    //formatters
    #tooltipFunction;
    #labelFormat;

    //#region =============== CHAINING METHODS (get/set) ================= 
    decimalPlaces(input) {
        /*
        Parameters 
        ----------------
        input (type: number)
          - Number of decimal places.
        */
        if (arguments.length === 0) {
            return this.#decimalPlaces;
        }
        else {
            const validNum = (typeof input == typeof 5) &&
                (input >= 0);

            if (validNum) {
                this.#decimalPlaces = input;
                return this;
            }
            else {
                console.error('decimalPlaces must be a number');
            }
        }
    }
    decimalType(input) {
        /*
        Parameters 
        ----------------
        input (type: number)
          - Number of decimal places.
        */
        let accepted = ['round', 'fixed']
        if (arguments.length === 0) {
            return this.#decimalType;
        }
        else {
            const valid = (typeof input == typeof 'abc' && accepted.includes(input.toLowerCase()));

            if (valid) {
                this.#decimalType = input;
                return this;
            }
            else {
                console.error('decimalType must be either "round" or "fixed"');
            }
        }
    }
    data(inputData) {
        /*
        Parameters 
        ----------------
        inputData (type: array)
          - An array of object(s) with 2+ fields per object
          - Each object represents one row of data. Each field represents a column
        */
        if (arguments.length === 0) {
            return this.#data;
        }
        else {
            // Check input
            const nonEmptyArray = (typeof inputData == typeof []) &&
                (inputData.length > 0);
            let validElements = true;

            if (nonEmptyArray) {
                for (let v of inputData) {
                    if ((typeof v != typeof {}) ||
                        Object.keys(v).length <= 1) {

                        validElements = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && validElements) {
                this.#data = inputData;
                return this;
            }
            else {
                console.error('Data must be an array of object(s) with at least 2 fields');
            }
        }
    }
    cKey(inputKey) {
        /*
        Parameters 
        ----------------
        inputKey (type: string)
          - A string representing a key that the data field has. 
          - This string should indicate the key (data header) for the independent variable
        */
        if (arguments.length === 0) {
            return this.#cKey;
        }
        else {

            const validString = (typeof inputKey == typeof 'abc') && inputKey;

            if (validString) {
                this.#cKey = inputKey;
                return this;
            }
            else {
                console.error('cKey must be a non-empty string');
            }
        }
    }
    nKey(inputKey) {
        /*
        Parameters 
        ----------------
        inputKey (type: string)
          - A string representing a key that the data field has. 
          - This string should indicate the key (data header) for the dependent variable
        */
        if (arguments.length === 0) {
            return this.#nKey;
        }
        else {

            const validString = (typeof inputKey == typeof 'abc') && inputKey;

            if (validString) {
                this.#nKey = inputKey;
                return this;
            }
            else {
                console.error('nKey must be a non-empty string');
            }
        }
    }
    graphTitle(inputTitle) {
        /*
        Parameters 
        ----------------
        inputTitle (type: string)
          - A string containing the title for the graph. 
        */

        if (arguments.length === 0) {
            return this.#graphTitle;
        }
        else {
            const validString = (typeof inputTitle == typeof 'abc') && inputTitle;

            if (validString) {
                this.#graphTitle = inputTitle;
                return this;
            }
            else {
                console.error('graphTitle must be a non-empty string');
            }
        }
    }
    transitionDuration(input) {
        if (arguments.length === 0) {
            return this.#transitionDuration;
        }
        else {
            const validNum = (typeof input === "number") &&
                (input >= 0);

            if (validNum) {
                this.#transitionDuration = input;
                return this;
            }
            else {
                console.error('transitionDuration must be a non-negative number');
            }
        }
    }
    width(inputWidth) {
        /*
        Parameters 
        ----------------
        inputWidth (type: number)
          - A non-negative number for the width of the bar graph.
        */
        if (arguments.length === 0) {
            return this.#width;
        }
        else {
            const validNum = (typeof inputWidth === "number") &&
                (inputWidth >= 0);

            if (validNum) {
                this.#width = inputWidth;
                return this;
            }
            else {
                console.error('width must be a non-negative number');
            }
        }
    }
    height(inputHeight) {
        /*
        Parameters 
        ----------------
        inputHeight (type: number)
          - A non-negative number for the height of the bar graph. 
        */

        if (arguments.length === 0) {
            return this.#height;
        }
        else {
            const validNum = (typeof inputHeight === "number") &&
                (inputHeight >= 0);

            if (validNum) {
                this.#height = inputHeight;
                return this;
            }
            else {
                console.error('height must be a non-negative number');
            }
        }
    }
    radius(input) {
        /*
        Parameters 
        ----------------
        inputHeight (type: number)
          - A non-negative number for the height of the bar graph. 
        */

        if (arguments.length === 0) {
            return this.#radius;
        }
        else {
            const validNum = (typeof input === "number") &&
                (input >= 0);

            if (validNum) {
                this.#radius = input;
                return this;
            }
            else {
                console.error('radius must be a non-negative number');
            }
        }
    }
    graphPosition(input) {
        /*
        Parameters 
        ----------------
        input (type: array)
          - [x, y] position of legend
        */
        if (arguments.length === 0) {
            return this.#graphPosition;
        }
        else {
            this.#graphPosition = input;
            return this;
        }
    }

    legendPosition(input) {
        /*
        Parameters 
        ----------------
        input (type: array)
          - [x, y] position of legend
        */
        if (arguments.length === 0) {
            return this.#legendPosition;
        }
        else {
            this.#legendPosition = input;
            return this;
        }
    }
    legendRadius(inputRadius) {
        /*
        Parameters 
        ----------------
        inputRadius (type: number)
          - A non-negative number for the radius of the legend circles.
        */
        if (arguments.length === 0) {
            return this.#legendRadius;
        }
        else {
            const validNum = (typeof inputRadius == typeof 5) &&
                (inputRadius >= 0);

            if (validNum) {
                this.#legendRadius = inputRadius;
                return this;
            }
            else {
                console.error('legendRadius must be a non-negative number');
            }
        }
    }
    legendTextOffset(inputOffset) {
        /*
        Parameters 
        ----------------
        inputOffset (type: number)
          - A number for the space between text and the legend circles.
        */
        if (arguments.length === 0) {
            return this.#legendTextOffset;
        }
        else {
            const validNum = (typeof inputOffset == typeof 5);

            if (validNum) {
                this.#legendTextOffset = inputOffset;
                return this;
            }
            else {
                console.error('legendTextOffset must be a number');
            }
        }
    }
    legendCircleSpacing(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing between legend circles.
        */
        if (arguments.length === 0) {
            return this.#legendCircleSpacing;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5);

            if (validNum) {
                this.#legendCircleSpacing = inputSpacing;
                return this;
            }
            else {
                console.error('legendCircleSpacing must be a number');
            }
        }
    }
    legendSpacingFromGraph(inputSpacing) {
        /*
        Parameters 
        ----------------
        inputSpacing (type: number)
          - A number for the spacing between the graph and the legend.
        */
        if (arguments.length === 0) {
            return this.#legendSpacingFromGraph;
        }
        else {
            const validNum = (typeof inputSpacing == typeof 5);

            if (validNum) {
                this.#legendSpacingFromGraph = inputSpacing;
                return this;
            }
            else {
                console.error('legendCircleSpacing must be a number');
            }
        }
    }
    legendOrientation(input) {
        /*
        Parameters 
        ----------------
        input (type: char)
          - A number for the spacing between the graph and the legend.
        */
        if (arguments.length === 0) {
            return this.#legendOrientation;
        }
        else {
            const valid = (typeof input == typeof 'a');

            if (valid) {
                this.#legendOrientation = input;
                return this;
            }
            else {
                console.error('legendOrientation must be "v" for vertical, or "h" for horizontal');
            }
        }
    }

    margins(inputMargins) {
        /*
        Parameters 
        ----------------
        inputMargins (type: array)
          - An array of numbers representing margins between the 
            bar graph and the SVG container. 
          - Specify margins in clockwise order (top, right, bottom, left)
        */
        if (arguments.length === 0) {
            return this.#margins;
        }
        else {
            // Validate nums
            let validNums = true;
            for (let n of inputMargins) {
                if (typeof n !== "number") {
                    validNums = false;
                    break;
                }
            }

            // Set fields
            if (validNums) {
                this.#margins = {
                    l: inputMargins[3],
                    r: inputMargins[1],
                    t: inputMargins[0],
                    b: inputMargins[2]
                };
                return this;
            }
            else {
                console.error(
                    'Please input an array of four numbers to configure top,' +
                    'right, bottom, and left margins in that order.'
                );
            }
        }
    }
    container(inputContainer) {
        /*
        Parameters 
        ----------------
        inputContainer (type: D3.js selection)
          - A SVG DOM element to render the bar graph in 
            (inputted as a d3.js selection)
        */
        if (arguments.length === 0) {
            return this.#container;
        }
        else {
            this.#container = inputContainer;
            return this;
        }
    }
    wrapper(inputWrapper) {
        /*
        Parameters 
        ----------------
        inputWrapper (type: D3.js selection)
          - A div containing the container element to render the 
            tooltips in (inputted as a d3.js selection)
        */
        if (arguments.length === 0) {
            return this.#wrapper;
        }
        else {
            this.#wrapper = inputWrapper;
            return this;
        }
    }
    table(inputTable) {
        /*
        Parameters 
        ----------------
        inputWrapper (type: D3.js selection)
          - A div to append the table to.
        */
        if (arguments.length === 0) {
            return this.#table;
        }
        else {
            this.#table = inputTable;
            return this;
        }
    }
    tableCaption(inputCaption) {
        /*
        Parameters 
        ----------------
        inputCaption (type: string)
          - A string containing the caption for the table. 
        */

        if (arguments.length === 0) {
            return this.#tableCaption;
        }
        else {
            const validString = (typeof inputCaption == typeof 'abc') && inputCaption;

            if (validString) {
                this.#tableCaption = inputCaption;
                return this;
            }
            else {
                console.error('tableCaption must be a non-empty string');
            }
        }
    }
    tableSummary(inputSummary) {
        /*
        Parameters 
        ----------------
        inputCaption (type: string)
          - A string containing the caption for the table. 
        */

        if (arguments.length === 0) {
            return this.#tableSummary;
        }
        else {
            const validString = (typeof inputSummary == typeof 'abc') && inputSummary;

            if (validString) {
                this.#tableSummary = inputSummary;
                return this;
            }
            else {
                console.error('tableSummary must be a non-empty string');
            }
        }
    }
    legendGroup(input) {
        if (arguments.length === 0) {
            return this.#legendGroup;
        }
        else {
            this.#legendGroup = input;
            return this;
        }
    }
    figureAriaLabel(input) {
        if (arguments.length === 0) {
            return this.#figureAriaLabel;
        }
        else {
            const validString = (typeof input == typeof 'abc') && input;

            if (validString) {
                this.#figureAriaLabel = input
                return this;
            }
            else {
                console.error('figureAriaLabel must be a non-empty string');
            }
        }
    }
    figureAriaDescription(input) {
        if (arguments.length === 0) {
            return this.#figureAriaDescription;
        }
        else {
            const validString = (typeof input == typeof 'abc') && input;

            if (validString) {
                this.#figureAriaDescription = input
                return this;
            }
            else {
                console.error('figureAriaDescription must be a non-empty string');
            }
        }
    }
    colourSeries(inputKeys) {
        /*
        Parameters 
        ----------------
        inputKeys (type: array)
          - An array of string(s) representing key(s) that the data field has currently selected. 
          - This array should indicate some key(s) to use for the numerical axis
        */

        if (arguments.length === 0) {
            return this.#colourSeries;
        }
        else {
            // Check input
            const nonEmptyArray = (typeof inputKeys == typeof []) &&
                (inputKeys.length > 0);
            let validElements = true;

            if (nonEmptyArray) {
                for (let v of inputKeys) {
                    if ((typeof v != typeof 'abc') || !v) {
                        validElements = false;
                        break;
                    }
                }
            }

            // Set field
            if (nonEmptyArray && validElements) {
                this.#colourSeries = inputKeys;
                return this;
            }
            else {
                console.error('colourSeries must be an array of non-empty string(s)');
            }
        }
    }
    colourScale(inputColourScale) {
        /*
        Parameters 
        ----------------
        inputCSubScale (type: function)
          - A d3.scaleOrdinal function that will be used to colour the bars.
        */
        if (arguments.length === 0) {
            return this.#colourScale;
        }
        else {
            this.#colourScale = inputColourScale;
            return this;
        }
    }

    captionAbove(inputToggle) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph tick text wrap/shrink to fit size.
        */

        if (arguments.length === 0) {
            return this.#captionAbove;
        }
        else {
            const validBool = (typeof inputToggle == typeof true);

            if (validBool) {
                this.#captionAbove = inputToggle;
                return this;
            }
            else {
                console.error('captionAbove must be a boolean');
            }
        }
    }
    isDataTable(inputToggle) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph tick text wrap/shrink to fit size.
        */

        if (arguments.length === 0) {
            return this.#isDataTable;
        }
        else {
            const validBool = (typeof inputToggle == typeof true);

            if (validBool) {
                this.#isDataTable = inputToggle;
                return this;
            }
            else {
                console.error('isDataTable must be a boolean');
            }
        }
    }
    tooltips(input) {
        /*
        Parameters 
        ----------------
        inputToggle (type: bool)
          - True to make the graph display region values. False otherwise.
        */
        if (arguments.length === 0) {
            return this.#tooltips;
        }
        else {
            const validBool = (typeof input == typeof true);

            if (validBool) {
                this.#tooltips = input;
                return this;
            }
            else {
                console.error('tooltips must be a boolean');
            }
        }
    }

    tooltipFunction(input) {
        if (arguments.length === 0) {
            return this.#tooltipFunction;
        }
        else {
            this.#tooltipFunction = input
            return this;
        }
    }

    labelFormat(input) {
        if (arguments.length === 0) {
            return this.#labelFormat;
        }
        else {
            this.#labelFormat = input;
            return this;
        }
    }

    hasRendered(input) {
        if (arguments.length === 0) {
            return this.#hasRendered;
        }
        else {
            this.#hasRendered = input
            return this;
        }
    }
    //#endregion

    //#region ============== PUBLIC (setup) ============== //
    initContainer() {
        /*
        Assigns the basic attributes to the container svg.
        
        Parameters
        ----------------
        undefined
        - Note: Requires height and width to have a value

        Returns
        ----------------
        undefined
        
        */

        this.#container
            // .attr('height', this.#height)
            .attr('width', '100%')
            .attr('viewBox', `0 0 ${this.#width} ${this.#height}`)
            .attr("perserveAspectRatio", "xMinyMin meet")
            .attr('aria-label', this.#figureAriaLabel)
            .attr('aria-description', this.#figureAriaDescription)
            .attr('tabindex', 0)

        let x;
        let y;

        if (this.#graphPosition) {
            x = this.#graphPosition[0];
            y = this.#graphPosition[1];
        }
        else {
            x = this.#width / 2;
            y = this.#height / 2;
        }

        this.#pieGroup = this.#pieGroup ?? this.#container.append('g')
            .attr('class', 'pie-group')
            .attr("transform", `translate(${x}, ${y})`);

        this.#invisPieGroup = this.#invisPieGroup ?? this.#container.append('g')
            .attr('class', 'invis-pie-group')
            .attr("transform", `translate(${x}, ${y})`);
    }
    initCValues() {
        this.#cValues = this.#data.map(el => el[this.#cKey])
    }
    initColourScale() {
        /*
        Initializes a scaleOrdinal for the colours of the bars.
        */
        this.#colourScale = d3
            .scaleOrdinal()
            .domain(this.#cValues)
            .range(this.#colourSeries)
    }
    initPie() {
        this.#pie = d3.pie()
            .sort(null)
            .value(d => d[this.#nKey])

        this.#inner = this.#radius * 0.4;
        this.#outer = this.#radius * 0.8;

        //used for donut/pie
        this.#arc = d3.arc()
            .outerRadius(this.#outer)
            .innerRadius(this.#inner);

        //to be used for outside labels
        this.#outerArc = d3.arc()
            .innerRadius(this.#radius)
            .outerRadius(this.#radius);
    }
    init() {
        this.initContainer();
        this.initCValues();
        this.initColourScale();
        this.initPie();

        return this;
    }
    render() {
        this.#renderPie();
        this.#renderInvisPie();
        this.#renderLegend();

        this.#setTabbing();

        if (this.#table) {
            this.#addTable();
        }

        this.#hasRendered;

        return this;
    }
    update() {
        this.#renderPie();
        this.#renderInvisPie();
        this.#renderLegend();

        if (this.#table) {
            this.#addTable();
        }
        return this;
    }
    magic() {
        this.init()

        this.#hasRendered ? this.update() : this.render()

        return this
    }
    //#endregion

    //#region ============== PRIVATE (logic) ============== //
    #midAngle(d) {
        return d.startAngle + (d.endAngle - d.startAngle) / 2;
    }
    #renderPie() {
        const that = this;

        function arcTween(d) {
            var i = d3.interpolate(this._current, d);
            this._current = i(0);
            return function(t) {
                return that.#arc(i(t));
            };
        }

        const arcs = this.#pieGroup
            .selectAll('.arc-group')
            .data(this.#pie(this.#data).map((el, i) => {
                el["order"] = i
                return el;
            }))
            .join(
                enter => {
                    let g = enter.append('g')
                        .attr('class', 'arc-group')
                        .attr('tabindex', -1);


                    //arc paths
                    g.append('path')
                        .each(function(d) {
                            this._current = {
                                startAngle: d.endAngle,
                                endAngle: d.endAngle
                            };
                        })
                        .attr('opacity', 1)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1)
                        .attrTween("d", arcTween)
                        .attr('fill', d => this.#colourScale(d.data[this.#cKey]))

                    //labels
                    let text = g.append('text');

                    text
                        .attr("transform", function(d) {
                            let pos = that.#outerArc.centroid(d);
                            pos[0] = that.#radius * (that.#midAngle(d) < Math.PI ? 1 : -1);
                            return "translate(" + pos + ")";
                        })
                        .attr("text-anchor", function(d) {
                            return that.#midAngle(d) < Math.PI ? "start" : "end";
                        })
                        .attr('dominant-baseline', 'middle')
                        .attr('opacity', 0)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1)

                    text
                        .text(function(d) {
                            return that.#getLabel(d.value);
                        });

                    //label lines
                    let polyline = g.append('polyline')
                        .attr("points", function(d) {
                            let pos = that.#outerArc.centroid(d);
                            pos[0] = that.#radius * 0.95 * (that.#midAngle(d) < Math.PI ? 1 : -1);
                            let p1 = that.#arc.centroid(d);
                            let p2 = that.#outerArc.centroid(d);
                            p2 = [p2[0] * 0.95, p2[1]]
                            let p3 = pos;
                            return [p1, p2, p3];
                        })
                        .attr('fill', 'none')
                        .attr('stroke', 'black')
                        .attr('opacity', 0)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1)
                },
                update => {
                    //arc paths
                    update.select('path')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('fill', d => this.#colourScale(d.data[this.#cKey]))
                        .attrTween("d", arcTween)

                    //labels
                    let text = update.select('text');

                    text
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr("transform", function(d) {
                            let pos = that.#outerArc.centroid(d);
                            pos[0] = that.#radius * (that.#midAngle(d) < Math.PI ? 1 : -1);
                            return "translate(" + pos + ")";
                        })
                        .attr("text-anchor", function(d) {
                            return that.#midAngle(d) < Math.PI ? "start" : "end";
                        })
                        .attr('dominant-baseline', 'middle')

                    text
                        .text(function(d) {
                            return that.#getLabel(d.value);
                        });

                    //label line
                    let polyline = update.select('polyline')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr("points", function(d) {
                            let pos = that.#outerArc.centroid(d);
                            pos[0] = that.#radius * 0.95 * (that.#midAngle(d) < Math.PI ? 1 : -1);
                            let p1 = that.#arc.centroid(d);
                            let p2 = that.#outerArc.centroid(d);
                            p2 = [p2[0] * 0.95, p2[1]]
                            let p3 = pos;
                            return [p1, p2, p3];
                        })
                },
                exit => {
                    //path
                    exit.select('path')
                        .datum(function(d, i) {
                            return {
                                startAngle: d.endAngle,
                                endAngle: d.endAngle
                            };
                        })
                        .transition()
                        .duration(this.#transitionDuration)
                        .attrTween("d", arcTween)
                        .on('end', () => {
                            //if exit transition ends, remove whole exit group
                            exit.remove()
                        })

                    //label
                    exit.select('text')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)

                    //label line
                    exit.select('polyline')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)
                }
            )
    }
    #renderInvisPie() {
        //render invisible (no transition) overlay of the piechart for tabbing/focus reasons (currently, tabbing to a pie region has clipping issues with focus)
        const that = this;

        function arcTween(d) {
            var i = d3.interpolate(this._current, d);
            this._current = i(0);
            return function(t) {
                return that.#arc(i(t));
            };
        }

        const arcs = this.#invisPieGroup
            .selectAll('.arc-group')
            .data(this.#pie(this.#data).map((el, i) => {
                el["order"] = i
                return el;
            }))
            .join(
                enter => {
                    let g = enter.append('g')
                        .attr('class', 'arc-group')
                        .attr('tabindex', -1)
                        .attr('aria-label', d => `${d.data[this.#cKey]}: ${d.value}`)
                    // .attr('opacity', 0);

                    //arc paths
                    g.append('path')
                        .each(function(d) {
                            this._current = {
                                startAngle: d.endAngle,
                                endAngle: d.endAngle
                            };
                        })
                        .attr('opacity', 0)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)
                        .attrTween("d", arcTween)
                    // .attr('fill', d => this.#colourScale(d.data[this.#cKey]))

                    //labels
                    let text = g.append('text');
                    text
                        .attr("transform", function(d) {
                            let pos = that.#outerArc.centroid(d);
                            pos[0] = that.#radius * (that.#midAngle(d) < Math.PI ? 1 : -1);
                            return "translate(" + pos + ")";
                        })
                        .attr("text-anchor", function(d) {
                            return that.#midAngle(d) < Math.PI ? "start" : "end";
                        })
                        .attr('dominant-baseline', 'middle')
                        .attr('opacity', 0)
                    // .transition()
                    // .duration(this.#transitionDuration)
                    // .attr('opacity', 0)

                    text
                        .text(function(d) {
                            return that.#getLabel(d.value);
                        });

                    //label lines
                    let polyline = g.append('polyline')
                        .attr("points", function(d) {
                            let pos = that.#outerArc.centroid(d);
                            pos[0] = that.#radius * 0.95 * (that.#midAngle(d) < Math.PI ? 1 : -1);
                            let p1 = that.#arc.centroid(d);
                            let p2 = that.#outerArc.centroid(d);
                            p2 = [p2[0] * 0.95, p2[1]]
                            let p3 = pos;
                            return [p1, p2, p3];
                        })
                        .attr('fill', 'none')
                        .attr('stroke', 'black')
                        .attr('opacity', 0)
                    // .transition()
                    // .duration(this.#transitionDuration)
                    // .attr('opacity', 0)
                },
                update => {
                    update.attr('aria-label', d => `${d.data[this.#cKey]}: ${d.value}`)

                    //arc paths
                    update.select('path')
                        .transition()
                        .duration(this.#transitionDuration)
                        // .attr('fill', d => this.#colourScale(d.data[this.#cKey]))
                        .attrTween("d", arcTween)

                    //labels
                    let text = update.select('text');
                    text
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr("transform", function(d) {
                            let pos = that.#outerArc.centroid(d);
                            pos[0] = that.#radius * (that.#midAngle(d) < Math.PI ? 1 : -1);
                            return "translate(" + pos + ")";
                        })
                        .attr("text-anchor", function(d) {
                            return that.#midAngle(d) < Math.PI ? "start" : "end";
                        })
                        .attr('dominant-baseline', 'middle')

                    text
                        .text(function(d) {
                            return that.#getLabel(d.value);
                        });

                    //label line
                    let polyline = update.select('polyline')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr("points", function(d) {
                            let pos = that.#outerArc.centroid(d);
                            pos[0] = that.#radius * 0.95 * (that.#midAngle(d) < Math.PI ? 1 : -1);
                            let p1 = that.#arc.centroid(d);
                            let p2 = that.#outerArc.centroid(d);
                            p2 = [p2[0] * 0.95, p2[1]]
                            let p3 = pos;
                            return [p1, p2, p3];
                        })
                },
                exit => {
                    //path
                    exit.select('path')
                        .datum(function(d, i) {
                            return {
                                startAngle: d.endAngle,
                                endAngle: d.endAngle
                            };
                        })
                        .transition()
                        .duration(this.#transitionDuration)
                        .attrTween("d", arcTween)
                        .on('end', () => {
                            //if exit transition ends, remove whole exit group
                            exit.remove()
                        })

                    //label
                    exit.select('text')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)

                    //label line
                    exit.select('polyline')
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 0)
                }
            )

        //add tooltips
        if (this.#tooltips) {
            this.#renderTooltips(this.#invisPieGroup
                .selectAll('.arc-group'));
        }
    }
    #renderTooltips(selection) {
        const data = this.#data;

        // console.log('tooltipSelection', selection)

        const tooltip = this.#wrapper.select(".tooltip").empty() ?
            this.#wrapper
            .append('div')
            .attr('class', 'tooltip')
            .attr('opacity', 0) :
            this.#wrapper.select(".tooltip")
        selection
            .on('mouseenter', (e, d) => {
                let html = '';

                // console.log(e, d, this.#data)

                // let myRegionId;
                // // if (typeof d === 'object') {
                // myRegionId = this.#data[d.properties[regionId]];
                // // } else {
                // //     myRegionId = d;
                // // }

                let colour = this.#colourScale(d.data[this.#cKey])
                if (this.#tooltipFunction) {
                    html = this.#tooltipFunction(d, colour);
                }
                else {
                    let spanAttr = `style="border-left:5px solid ${colour}; padding-left:3px; display:block"`;
                    // html += `` + this.#getDisplayValue(this.#data, d);
                    html += `<span ${spanAttr}>` + d.value;
                    html += '</span>';
                }


                tooltip.html(html)
                    .style('opacity', 1)
                    .style("display", "block")
            })
            .on('mouseleave', function(e, d) {
                tooltip
                    .style('opacity', 0)
                    .style("display", "none")
            })
            .on('mousemove', function(e, d) {
                tooltip
                    .style("transform", `translateX(25px)`)
                    .style("left", `${(e.clientX)}px`)
                    .style("top", `${(e.clientY)}px`)
            })
    }
    #round(number) {
        if (!isNaN(this.#decimalPlaces)) {
            let multiplier = Math.pow(10, this.#decimalPlaces)
            return Math.round(number * multiplier) / multiplier
        }
        else {
            return number;
        }
    }
    #getLabel(value) {
        let newValue;

        if (this.#labelFormat) {
            return this.#labelFormat(value)
        }
        newValue = this.#round(value)
        if (this.#decimalType == "fixed") {
            newValue = newValue.toFixed(this.#decimalPlaces)
        }
        if (isNaN(newValue)) {
            return value;
        }
        return newValue;
    }
    #setTabbing() {
        //set tabbing and focus based rules like other modular versions
        this.#container.on('keydown', e => {
                const isContainer = e.target.id == this.#container.attr('id');
                let pieGroups = this.#invisPieGroup.selectAll('.arc-group')
                let pieArr = Array.from(pieGroups._groups[0]);
                if (e.key == 'Enter') {
                    if (isContainer) {
                        pieGroups.attr('tabindex', 0);
                        pieGroups.node().focus();
                    }
                }
                else if (e.key == 'Escape') {
                    pieGroups.attr('tabindex', -1);
                    this.#invisPieGroup.node().focus();
                }
                else if (e.key == "Tab") {
                    let decompIndex = pieArr.indexOf(e.target)
                    if (!e.shiftKey && decompIndex == pieArr.length - 1) {
                        // console.log("leave bar forwards")
                        pieGroups.attr('tabindex', -1);
                    }
                    else if (e.shiftKey && decompIndex == 0) {
                        // console.log("leave bar backwards")
                        pieGroups.attr('tabindex', -1);
                    }
                }
            })
            .on('click', (e) => {
                let pieGroups = this.#invisPieGroup.selectAll('.arc-group')
                let pieArr = Array.from(pieGroups._groups[0]);
                if (pieArr.includes(e.target.parentNode)) {
                    pieGroups.attr('tabindex', 0);
                }
            })
            .on('focusout', (e) => {
                let pieGroups = this.#invisPieGroup.selectAll('.arc-group')
                let pieArr = Array.from(pieGroups._groups[0]);
                if (!pieArr.includes(e.relatedTarget)) {
                    // console.log('focusout')
                    pieGroups.attr('tabindex', -1);
                }
            })
    }
    #renderLegend() {
        if (!this.#legendGroup)
            this.#legendGroup = this.#container.append('g').attr('class', 'legend')
        const legend = this.#legendGroup;
        // console.log(this.#data)

        let legendPosition = this.#legendPosition ? this.#legendPosition : [0, 0];

        legend.selectAll('g.legend-group')
            .data(this.#data)
            .join(
                (enter) => {
                    let g = enter.append('g')
                        .attr('class', 'legend-group')
                        .attr('tabindex', -1);

                    //circle
                    let circle = g.append('circle')
                        .attr('r', this.#legendRadius)
                        .attr('cx', (d, i) => {
                            return legendPosition[0] + (this.#legendOrientation == 'v' ? 0 : this.#legendCircleSpacing * i)

                        })
                        .attr('cy', (d, i) => {
                            return legendPosition[1] + (this.#legendOrientation == 'v' ? this.#legendCircleSpacing * i : 0)
                        })
                        // .attr('class', d => categoryLookup[d])
                        .attr('opacity', 0)
                        .attr('fill-opacity', 0)
                        .attr('fill', (d, i) => {
                            // console.log(d)
                            let myColour = this.#colourScale(d[this.#cKey]);
                            // if (this.#textures && this.#textureSeries[i] != 'solid') {
                            //     return this.#textureSeries[i].url();
                            // }
                            return myColour;
                        })
                        .classed('selected', true)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1)
                        .attr('fill-opacity', 1)

                    //text
                    let text = g.append('text')
                        // .attr('class', d => categoryLookup[d])
                        .attr('alignment-baseline', 'middle')
                        .attr('dominant-baseline', 'middle')
                        .attr('x', (d, i) => {

                            let spacing
                            if (i == 0) {
                                spacing = 0;
                            }
                            else {
                                spacing = this.#legendCircleSpacing * i
                                // + legendGroupBoundings.filter((el, index) => index < i).reduce((partialSum, el) => partialSum + el.width, 0)
                            }
                            return legendPosition[0] + this.#legendTextOffset + (this.#legendOrientation == 'v' ? 0 : spacing)

                        })
                        .attr('y', (d, i) => legendPosition[1] + (this.#legendOrientation == 'v' ? this.#legendCircleSpacing * i : 0))
                        .attr('opacity', 0)
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1)

                    text.text(d => d[this.#cKey])
                    // if (this.#interactive) {
                    //     circle.attr('cursor', 'pointer')
                    //     text.attr('cursor', 'pointer')
                    // }
                },
                (update) => {
                    //circle
                    let circle = update.select('circle')
                        // .attr('class', d => categoryLookup[d])
                        .classed('selected', true)
                        // .attr('opacity', 0)
                        .attr('opacity', function(d) {
                            let selection = d3.select(this.parentNode)
                            if (selection.text() == d) {
                                return d3.select(this).attr('opacity')
                            }
                            return 0
                        })
                        .attr('fill-opacity', 1)
                        .attr('fill', (d, i) => {
                            let myColour = this.#colourScale(d[this.#cKey]);
                            // if (this.#textures && this.#textureSeries[i] != 'solid') {
                            //     return this.#textureSeries[i].url();
                            // }
                            return myColour
                        })
                        .attr('r', this.#legendRadius)
                        .attr('cx', (d, i) => {
                            let spacing
                            if (i == 0) {
                                spacing = 0;
                            }
                            else {
                                spacing = this.#legendCircleSpacing * i
                            }
                            return legendPosition[0] + (this.#legendOrientation == 'v' ? 0 : spacing)
                        })
                        .attr('cy', (d, i) => {
                            return legendPosition[1] + (this.#legendOrientation == 'v' ? this.#legendCircleSpacing * i : 0)

                        })
                        .transition().duration(this.#transitionDuration)
                        .attr('opacity', 1)


                    //text
                    let text = update.select('text')
                        // .attr('class', function(d) {
                        //     return categoryLookup[d];
                        // })
                        .attr('opacity', function(d) {
                            let selection = d3.select(this)
                            if (selection.text() == d) {
                                return selection.attr('opacity')
                            }
                            return 0
                        })
                        // .attr('opacity', 0)
                        .text(d => d[this.#cKey])

                    text
                        .attr('x', (d, i) => {

                            let spacing
                            if (i == 0) {
                                spacing = 0;
                            }
                            else {
                                spacing = this.#legendCircleSpacing * i
                                // + legendGroupBoundings.filter((el, index) => index < i).reduce((partialSum, el) => partialSum + el.width, 0)
                            }
                            return legendPosition[0] + this.#legendTextOffset + (this.#legendOrientation == 'v' ? 0 : spacing)

                        })
                        .attr('y', (d, i) => legendPosition[1] + (this.#legendOrientation == 'v' ? this.#legendCircleSpacing * i : 0))
                        .transition()
                        .duration(this.#transitionDuration)
                        .attr('opacity', 1)


                    // if (this.#interactive) {
                    //     circle.attr('cursor', 'pointer')
                    //     text.attr('cursor', 'pointer')
                    // }
                },
                (exit) => {
                    // exit.select('text')
                    //   .transition()
                    //   .duration(this.#transitionDuration)
                    //   .attr('opacity', 0)

                    // exit.select('circle')
                    //   .transition()
                    //   .duration(this.#transitionDuration)
                    //   .attr('opacity', 0)
                    //   .on('end', () => exit.remove())
                    exit.remove()
                }
            )
    }
    #addTable() {
        let data = this.#data;
        // console.log('tableData', this.#data)
        /*
          Adds a table to the #table property. Contains the standard classes typically used on infobase products.
          
          Note: uses #table, #tableSummary, #tableDetails, #data, #cSeries, #categories
        */

        const tableExists = !this.#table.select('details').empty();

        let tableDetails;

        if (tableExists) {
            this.#table.select('details').selectAll("*").remove();
            tableDetails = this.#table.select('details');
        }
        else {
            tableDetails = this.#table.append('details');
        }

        // let tableID = this.#table.attr('id') + "-table";


        tableDetails.append("summary").text(this.#tableSummary)

        // visual caption
        if (this.#tableCaption && this.#captionAbove)
            tableDetails.append('p')
            .attr('aria-hidden', true)
            .attr('class', 'caption')
            .text(this.#tableCaption)

        const tableContainer = tableDetails.append("div").attr("class", "table-responsive")
        const table = tableContainer.append("table")
            // .attr('id', tableID)
            .attr("class", "wb-table table table-bordered table-striped table-hover")

        if (this.#tableCaption) {
            let caption = table.append('caption')
                .text(this.#tableCaption)

            caption.classed('wb-inv', this.#captionAbove)
        }

        const tr = table.append('thead').append('tr').attr('class', 'bg-primary')
        // let tableArr = this.#data.columns;
        let tableArr = []
        tableArr.push(this.#cKey)
        // if (this.#categoryKey) {
        //   tableArr.push(this.#categoryKey)
        // }
        tableArr.push(this.#nKey)
        // if (this.#displayUncertainties) {
        //   tableArr.push(this.#upperUncertainty)
        //   tableArr.push(this.#lowerUncertainty)
        // }
        // tableArr.push(this.#cKey)
        // tableArr = tableArr.concat(this.#categories)

        tableArr.map(el => {
            tr.append('th')
                // .style("vertical-align", "top").attr('scope', 'col')
                .text(() => {
                    return this.#tableHeaderFunction ? this.#tableHeaderFunction(el) : el
                })
        })

        const tbody = table.append("tbody")

        let language = d3.select('html').attr('lang');

        this.#data.map(row => {
            let tr = tbody.append("tr")

            tableArr.map(el => {
                tr.append('td')
                    .attr('data-sort', () => {
                        let text = row[el]
                        let number = parseFloat(text)
                        if (!isNaN(number)) {
                            return number
                        }
                    })
                    .html(() => { //security would be better as .text, but want to be able to insert html
                        let text = row[el]
                        if (this.#tableCellFunction) {
                            text = this.#tableCellFunction(text, row, el)
                        }

                        if (!isNaN(text)) {
                            let value = parseFloat(text)
                            if (!isNaN(this.#decimalPlaces)) {
                                value = this.#round(value)
                                if (this.#decimalType == "fixed" && this.#decimalPlaces) {
                                    value = value.toFixed(this.#decimalPlaces)

                                }
                                // console.log(value, this.#decimalPlaces)
                            }

                            return language == 'fr' ? (value + "").replace('.', ',') : value;
                            // return value
                        }

                        return text
                    })
            })
        })
        // console.log("---------", table)
        // $('#' + tableID).DataTable();

        if (this.#isDataTable) {
            if (language == 'en') {
                $(table.node()).DataTable();
            }
            else {
                $(table.node()).DataTable({
                    "language": {
                        "sProcessing": "Traitement en cours...",
                        "sSearch": "Rechercher&nbsp;:",
                        "sLengthMenu": "Afficher _MENU_ &eacute;l&eacute;ments",
                        "sInfo": "Affichage de l'&eacute;lement _START_ &agrave; _END_ sur _TOTAL_ &eacute;l&eacute;ments",
                        "sInfoEmpty": "Affichage de l'&eacute;lement 0 &agrave; 0 sur 0 &eacute;l&eacute;ments",
                        "sInfoFiltered": "(filtr&eacute; de _MAX_ &eacute;l&eacute;ments au total)",
                        "sInfoPostFix": "",
                        "sLoadingRecords": "Chargement en cours...",
                        "sZeroRecords": "Aucun &eacute;l&eacute;ment &agrave; afficher",
                        "sEmptyTable": "Aucune donn&eacute;e disponible dans le tableau",
                        "oPaginate": {
                            "sFirst": "Premier",
                            "sPrevious": "Pr&eacute;c&eacute;dent",
                            "sNext": "Suivant",
                            "sLast": "Dernier"
                        },
                        "oAria": {
                            "sSortAscending": ": activer pour trier la colonne par ordre croissant",
                            "sSortDescending": ": activer pour trier la colonne par ordre d&eacute;croissant"
                        }
                    },
                });
                table.on('click', 'th', function() {
                    let tableID = table.attr('id');
                    $("#" + table.attr('id') + " th").addClass("sorting")
                    //$(this).removeClass("sorting")
                });
            }
        }

        // $('#' + tableID).trigger("wb-init.wb-tables")
        // $( ".wb-tables" ).trigger( "wb-init.wb-tables" );
    }
    //#endregion
}
"""
        documentation = """// Documentation is currently just this example
import { PieChart } from "/src/js/modular/pie.js";

//Load Data
var dataFiles = [
    "./data/dummy.csv", //0
    "./data/dummy2.csv", //1
]
var promises = [];
dataFiles.forEach(function(url) {
    if (url.match(/.*\.csv$/gm)){
        promises.push(d3.csv(url))
    }
    else if (url.match(/.*\.json$/gm)){
        promises.push(d3.json(url))
    }
});
Promise.all(promises).then(function(values) {
    console.log('myData', values)
    
    //make pie :D
    let pie = new PieChart();
    
    pie
        .wrapper(d3.select('#pieWrapper'))
        .container(d3.select('#pie'))
        .data(values[0])
        .cKey("country")
        .nKey("val1")
        // .radius(200)
        .graphPosition([240, 240])
        .legendPosition([500, 50])
        // .legendOrientation('h')
        .init()
        .render()
        
    
    
    let toggle = true;
    
    d3.select("#updatePie").on("click", () => {
        if (toggle) {
            pie
            .wrapper(d3.select('#pieWrapper'))
            .container(d3.select('#pie'))
            .data(values[1])
            .cKey("region")
            .nKey("cars")
            .init()
            .update()
        }
        else {
            pie
            .wrapper(d3.select('#pieWrapper'))
            .container(d3.select('#pie'))
            .data(values[0])
            .cKey("country")
            .nKey("val1")
            .init()
            .update()
        }
        toggle = !toggle
    })
})"""

    return llm.invoke({'question': query, 'source': source, 'documentation': documentation})

def main(query: str, graph_type: str):
    # Load data
    llm = load_llm(ANTHROPIC_KEY)

    # Search
    answer = generate_answer(query, graph_type, llm)
    return answer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Your question about the modular code")
    parser.add_argument("-g", "--graph", help="The type of graph you're working with ('bar', 'line', 'map', or 'pie')", type=str, default='bar')

    args = parser.parse_args()
    answer = main(args.query, args.graph)
    print(answer.content)