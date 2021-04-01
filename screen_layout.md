- [Screen Layout](#screen-layout)
  * [Category Settings](#category-settings)
    + [Effects](#effects)
  * [Screen Settings](#screen-settings)
  * [Table Settings](#table-settings)
    + [Wrap-Around Table](#wrap-around-table)
    + [Horizontal Table](#horizontal-table)
    + [Examples](#examples)
  * [Counter Settings](#counter-settings)
    + [Examples](#examples-1)

# Screen Layout
A dictionary to represent the layout of items on your screen. A category item must be defined for each item you wish to display on the screen.

The mpcurses repository contains several [examples](https://github.com/soda480/mpcurses/tree/master/examples), refer to the example screen layouts to gain a better understanding of the settings described below.

**Note**: For category items requiring color codes; refer to the [Colors Script](https://github.com/soda480/mpcurses/blob/master/examples/colors.py) for a visual of supported codes and their colors.

## Category Settings
Categories must be unique strings and their value is a dictionary and comprised of the following items:

Name | Required | Type | Description
-- | -- | -- | --
position | required | tuple | A tuple (y, x) representing the position on the screen where the item is to be displayed. |
text | optional | str | The static text to display on the screen at the given **position**. |
text_color | optional | int | The 256 color RGB value to assign the static text.<br /><br />Required if **text** is specified. |
regex | optional | str | A regex expression to match a log message; if using a named group then you must name the group `value`. If matched then the matched value is displayed otherwise the matched message is displayed. |
length | optional | int | If **regex** is matched then display length characters of matched value. This is suitable when the matched value is long and may not display neatly on the screen. The **Default value** is 100 characters with '...' appended at the end.<br /><br />Only valid if used with **regex**. |
right_justify | optional | bool | If **regex** is matched then display the matched value right-justified.<br /><br />Only valid if used with **regex**. |
color | optional | int | If **regex** is matched then display the matched value with the specified 256 color RGB value.<br /><br />Only valid if used with **regex**. |
replace_text | optional | str | If **regex** is matched then replace the matched value with the provided string.<br /><br />Only valid if used with **regex**.|
clear | optional | bool | If **regex** is matched then clear the current string at **position** prior to displaying the matched value.<br /><br />Only valid if used with **regex**. |
keep_count | optional | bool | If **regex** is matched then keep and display the current count of the number of matches.<br /><br />Only valid if used with **regex**.|
zfill | optional | int | Add zeros to the beginning of the count until it reaches the specified length.<br /><br />Only valid if used with **keep_count**. |
effects | optional | list | List of effects represented as dictionaries that will be processed on the matched value.[See Effects](#effects) for specification.<br /><br />Only valid if used with **regex**. |
table | optional | bool | Designates the position is determined from the **position** assigned and the respective process offset. Each spawned process is assigned its own unique offset, i.e. `Process1` is assigned offset 0, `Process2` is assigned offset 1, etc. When a category is matched, its vertical position on the screen is calculated by adding the position y value with the process offset.<br /><br />This should only be set if running multiple processes, this has the effect of displaying matched values from multiple processes where each process is displayed on its own row. If you wish to display table data horizontally or using a wrap-around technique then you need to supply additional configuration [See Table Settings](#table-settings).<br /><br />Only valid if used with **regex** |
list | optional | bool | Designates that the matched value should appear to be added to a list on the screen. Specifically, the value of **keep_count** is added to the position y value to display the matched value to the screen. This has the effect of displaying items as a list when matched.<br /><br />Should not be used if **table** is set.<br /><br />Only valid if used with **keep_count**.|
padding | optional | int | Number of characters (i.e. spacing) between process offsets in a horizontal table. Specifically, the horizontal position is determined by multiplying this value with the process offset and adding it to the specified position x value.<br /><br />Only valid if used with horizontal table orientation.<br /><br />Only valid if used with **regex**.|

### Effects
Name | Required | Type | Description
-- | -- | -- | --
regex | required | str | A regex expression to match the matched value. This is useful if you wish to change the color of matched value depending on the value, i.e. if matched value is 'passed' then change color to green, if 'failed' then change color to red, etc. |
color | required | int | If **regex** is matched then display the matched value with the specified 256 color RGB value.<br /><br />Only valid if used with **regex**. |

## Screen Settings
You may configure default screen settings using the reserved category key `_screen`. The value must be a dictionary and comprised of the following items:

Name | Required | Type | Description and Default Value
-- | -- | -- | --
title | optional | str | If specified will display the specified string centered on the first line of the screen.<br /><br />**Default value**: the name of the program being executed. |
color | optional | int | The 256 color RGB value to assign the title text. |
blink | optional | bool | Specify if MPcurses should enabling blinking effect, when enabled a 'RUNNING..." message is blinked on the upper left hand-side of the screen.<br /><br />**Default value**: True |
show_process_status | optional | bool | Specify if MPcurses should display the process status in the lower left hand-side of the screen. The items that will be displayed are: # of processes Running, Queued and Completed.<br /><br />**Default value**: True if any processes will be queued, False otherwise. For example, if you specified a **processes_to_start** value of 5 but the total number of processes is 20, then this value will be True. |
zfill | optional | int | Add zeros to the beginning of the process status counts until it reaches the specified length.<br /><br />**Default value**: Number of digits for the total number of processes being executed. For example, if running 100 processes then this value is set to 3, if 20 processes then 2, etc. |

## Table Settings
Configure wrap-around or horizontal table settings using the reserved category key `table`. This should **only** be set if you wish to format your table as a wrap-around or horizontal table. The value must be a dictionary and comprised of the following settings, see below.

### Wrap-Around Table
Display data from processes vertically in their own row, if row limit is reached then wrap the table horizontally.

![wraparound](https://raw.githubusercontent.com/soda480/doc/master/wraparound.png)

### Horizontal Table
Display data from processes horizontally in their own column.

![horizontal](https://raw.githubusercontent.com/soda480/doc/master/horizontal.png)

Name | Required | Type | Description
-- | -- | -- | --
orientation | optional | str | Designates the orientation of the table, possible values are `wrap_around` or `horizontal`.<br /><br />**Default value**: `wrap_around` |
rows | optional | int | Number of rows in the wrap around table.<br /><br />Only valid if used with `wrap_around` table orientation. |
cols | optional | int | Number of columns in the wrap around table. Note that a column can consist of multiple headers.<br /><br />Only valid if used with `wrap_around` table orientation. |
width | optional | int | Number of characters (i.e. spacing) between headers from process offsets that are spanned horizontally.<br /><br />Only valid if used with `wrap_around` table orientation. |
squash | optional | bool | Specify it wrap around table should be squashed if the number of processes are less than the number of **rows** specified. This has the effect of formatting the wrap around table to fit nicely on the screen when the total number of processes are less than the number of rows specified.<br /><br />Only valid if used with `wrap_around` table orientation.<br /><br />**Default value**: `False`|
padding | optional | int | Number of characters (i.e. spacing) between process offsets in a horizontal table.<br /><br />Only valid if used with `horizontal` table orientation. |

### Examples
An example of a horizontal table can be seen in [example2](https://github.com/soda480/mpcurses/blob/master/examples/example2.py)

An example of a wrap-around table can be seen in [example6](https://github.com/soda480/mpcurses/blob/master/examples/example6.py)

## Counter Settings
Counter settings can be used to further refine how matched categories are counted (i.e. visualized) on the screen. They can provide the means to further visualize progress of execution. Counter settings are provided using the reserved category key `_counter_`. The value must be a dictionary and comprised of the following settings:

Name | Required | Type | Description
-- | -- | -- | --
position | required | tuple | A tuple (y, x) representing the position on the screen where the counter is to be displayed. |
categories | required | list | The list of categories to count, the categories **must** already exist and have **keep_count** set in their configuration. |
counter_text | required | str | Designate that the specified text to be displayed on the screen instead of the category count. |
color | optional | int | Display the **counter_text** with the specified 256 color RGB value.<br /><br />Required if **modulus** is specified.|
modulus | optional | int | Designate whether a modulus should be used to determine when the **counter_text** should be displayed. Display counter_text for every X amount of counts for the given category. |
width | optional | int | The total width for the **counter_text** before wrapping to the next line. |
table | optional | bool | Designates the position is determined from the **position** and the respective process offset. The vertical position is calculated by adding the position y value with the process offset. |
regex | optional | str | A regex expression to match to determine the total possible number of items to be processed; use this if you wish to add a progress bar style display.<br /><br />Requires **modulus** setting. |

### Examples
An example of counters can be seen in [example_counter1](https://github.com/soda480/mpcurses/blob/master/examples/example_counter1.py)

An example of counters using a modulus can be seen in [example_counter2](https://github.com/soda480/mpcurses/blob/master/examples/example_counter2.py)

An example of counters using a progress bar can be seen in [example_counter3](https://github.com/soda480/mpcurses/blob/master/examples/example_counter3.py)
