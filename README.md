# Spreadsheet2Roll20

## Usage

Download your spreadsheet in `.html`. Then, process the file.

```shell
$ pip install -r requirements.txt
$ python3 main.py --filename input/sheet.html
```

Write `<< YOUR_SCRIPT >>` in the spreadsheet. This program will automatically eval your script.


## Functions

### INPUT

```python
INPUT(
    attr_name: str,
    input_type: str,
    value: str = "",
    attributes: dict = None
)
```
Refer https://wiki.roll20.net/Building_Character_Sheets#Storing_User_Data 

### BUTTON
```python
BUTTON(
    roll_name: str,
	value: str,
    attributes: dict = None
)
```
Refer https://wiki.roll20.net/Button

### TEXTAREA
```python
TEXTAREA(
	attr_name: str,
	attributes: dict = None
)
```
### SELECT
```python
SELECT(
	attr_name: str,
	values: list,
	attributes: dict = None
)
```
Refer https://wiki.roll20.net/Building_Character_Sheets#Dropdown_menu
