import re


class Pattern():
    # Begin language tag "<language id=''>"
    # INPUT: "<root>  <language id="english">    <entr"
    # Finds: "<language id="english">"
    language_start = re.compile(r"<language id=.*?(?=>).")

    # End language tag "</language"
    language_exit = re.compile(r"<\/language>")

    # Begin entry tag "<entry"
    entry_start = re.compile(r"(<entry)")

    # End entry tag "</entry"
    entry_exit = re.compile(r"(<\/entry>)")

    # Begin AND end entry tag (multi-line support)
    entry = re.compile(r"<entry.*?(?=entry>)entry>")

    # Get the value of entry id
    entry_id = re.compile(r"<entry id(?:.*\"(.*)\")(?=><)")

    # Get data from localization entries with well-formed CDATA
    # -- Example --
    # INPUT: "<entry id="name"><![CDATA[text[that may look]] like this]]></entry>"
    # Finds: "text[that may look]] like this"
    cdata = re.compile(r"\[.*\[(.*)\]{2}(?=></)")

    # Get all text in the entry field.
    # -- Example --
    # INPUT: "<entry id="name"><![CDATA[text[that may look]] like this]]></entry>"
    # Finds: "><![CDATA[text[that may look]] like this]]"   <--- Remember that "><" are included as well (TODO: fix that)
    cdata_fix = re.compile(r"><.*(?=></)")

    # Get data from localization entries with malformed CDATA
    # Well-formed: "[CDATA[text[that may look]]"
    # Works on:    "CDATAtextthat may look     <--- Missing any "[" and "]"
    # Finds:       "textthat may look"
    malformed_cdata = re.compile(r"\[?CDATA\[?(.*?)(?=]{0,2}></)")

    # Split text and color codes. Works on all text/color code pairs in INPUT
    # -- Example --
    # INPUT: "{colour_start|huixiang}检测到程序错误！{colour_end}"
    # begin_color: "{colour_start|huixiang}"
    # text:        "检测到程序错误！"
    # end_color:   "{colour_end}"
    color_codes = re.compile(r"(?P<start_color>{.*?})(?P<text>.*?)(?P<end_color>{.*?})")