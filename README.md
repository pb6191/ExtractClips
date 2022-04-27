# Example usage

App link: https://gpng.herokuapp.com/

Run Flask app locally: `python main.py`

## Basic Usage (no options checked)

Enter one headline/url per line to generate a card/image for each headline/url. If you save the urls as separate rows in a spreadsheet, you can simply copy that column and paste it to the app. See this [Google Sheets for an example](https://docs.google.com/spreadsheets/d/1vWyNththog-n5oOV18i4kj_hlUEsFkqI9KhCO3p3O2I/edit?usp=sharing).

```
https://www.glamour.com/story/megan-fox-and-machine-gun-kelly-relationship-timeline
https://www.nytimes.com/2022/01/04/business/economy/job-openings-coronavirus.html
https://www.foxnews.com/entertainment/betty-white-great-spirits-filming-tribute-fans
```

## Reduce font size

Check this box to reduce the font size of the headline and description texts.

## Replace Headlines (replace headline text)

Replaces headline text with new text. Each line is a headline url and the text to replace the existing text, separated by a tab. The easiest way to use this option is to create a spreadsheet with two columns (headline url, new headline text), copy the contents of the two columns, and paste them into the app. This approach will ensure the required tabs are inserted properly. See this [Google Sheets for an example](https://docs.google.com/spreadsheets/d/1vWyNththog-n5oOV18i4kj_hlUEsFkqI9KhCO3p3O2I/edit?usp=sharing). 

Note: This option replaces only the headline text but not the description text.

```
https://www.url1.com	headline1
https://www.url2.com	headline2
```

## Replace Images

Replaces image with images (specified as urls). Each line is a headline url and a url to an image separated by a tab. As with `Replace Headlines`, the easiest way to use this option is to create a spreadsheet with two columns (headline url, image url), copy the contents of the two columns, and paste them into the app. This approach will ensure the required tabs are inserted properly. See this [Google Sheets for an example](https://docs.google.com/spreadsheets/d/1vWyNththog-n5oOV18i4kj_hlUEsFkqI9KhCO3p3O2I/edit?usp=sharing). 

```
https://www.url1.com	https://www.newimage1.jpeg
https://www.url2.com	https://www.newimage2.jpeg
```

## Replace Headlines and Images

Replace headline text and image at the same time by checking both boxes. As with `Replace Headlines` and `Replace Images`, create a spreadsheet with three columns (headline, new text, new image url), copy the contents of the three columns, and paste them into the app. This approach will ensure the required tabs are inserted properly. See this [Google Sheets for an example](https://docs.google.com/spreadsheets/d/1vWyNththog-n5oOV18i4kj_hlUEsFkqI9KhCO3p3O2I/edit?usp=sharing). 

```
https://www.url1.com	headline1	https://www.newimage1.jpeg
https://www.url2.com	headline2	https://www.newimage2.jpeg
```


