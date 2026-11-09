"""Build the PDF write-up (report.pdf) from the script output and figures."""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (Image, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["BodyText"], fontSize=10.5, leading=14.5)
h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, spaceAfter=4)
sub = ParagraphStyle("sub", parent=ss["Normal"], alignment=TA_CENTER, fontSize=12,
                     textColor=colors.HexColor("#444444"), spaceAfter=14)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13.5, spaceBefore=10)
h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontSize=11, spaceBefore=6)
code = ParagraphStyle("code", fontName="Courier", fontSize=7.6, leading=9.4,
                      backColor=colors.HexColor("#f4f4f4"), borderPadding=5,
                      leftIndent=4, rightIndent=4)
cap = ParagraphStyle("cap", parent=body, fontSize=9, textColor=colors.HexColor("#555555"),
                     alignment=TA_CENTER, spaceAfter=8)


def header_footer(c, doc):
    c.saveState()
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(2 * cm, A4[1] - 1.2 * cm, "Data Handling with Python")
    c.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm,
                      "Assignment: Cleaning and Visualising Data")
    c.drawCentredString(A4[0] / 2, 1.1 * cm, str(doc.page))
    c.restoreState()


def fig(name, caption, width=13.5 * cm):
    path = os.path.join(FIG, name)
    iw, ih = ImageReader(path).getSize()
    return [Image(path, width=width, height=width * ih / iw), Paragraph(caption, cap)]


def P(t, s=body):
    return Paragraph(t, s)


output = open(os.path.join(HERE, "output.txt")).read()
source = open(os.path.join(HERE, "assignment.py")).read()

story = [
    P("Cleaning and Visualising Data", h1),
    P("Missing Values, Scatter Plots, and Interpretation", sub),
    Table([["Name:", "______________________", "Date:", "______________"]],
          colWidths=[1.6 * cm, 6 * cm, 1.4 * cm, 4 * cm],
          style=TableStyle([("FONTSIZE", (0, 0), (-1, -1), 10.5)])),
    Spacer(1, 10),

    P("The data", h2),
    P("Instead of the 15-row example matrix, the assignment uses the file "
      "<i>export_english.csv</i>: weekly COVID-19 case counts for 2020&ndash;2022, "
      "8,753 rows, split by health region, area, sex, age group and socioeconomic "
      "index. Each row also gives the population of that group. Every observation is "
      "stored as <b>[x, y] = [population, cases]</b>. A third column, "
      "<b>socioeconomic_index</b>, is kept as well, to show that <font name='Courier'>"
      "clean_matrix</font> works for any number of columns."),
    P("The file has no empty cells, but it does have missing values, coded in "
      "two ways. These are turned into Python missing values when the file is loaded:"),
    Table([
        ["Raw value in the CSV", "Meaning", "Loaded as", "Rows"],
        ["socioeconomic_index = -1", "the source's code for \"unknown\"", "None", "94"],
        ["population = 0 (with cases > 0)", "unknown group (sex/age \"Not available\")", "NaN", "11"],
        ["empty cell", "blank entry", '""', "0"],
    ], colWidths=[4.8 * cm, 5.9 * cm, 2.2 * cm, 1.4 * cm], style=TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
    ])),

    P("Task 1: Clean the matrix", h2),
    P("<font name='Courier'>is_missing(v)</font> returns True for <font name='Courier'>"
      "None</font>, for float NaN (checked with <font name='Courier'>math.isnan</font> "
      "after <font name='Courier'>None</font> and strings are ruled out), and for empty "
      "or whitespace-only strings. <font name='Courier'>clean_matrix(matrix, fill=-1)"
      "</font> deep-copies the input, loops over every cell, swaps each missing value "
      "for <font name='Courier'>fill</font>, and returns the new matrix together with "
      "the list of (row, column) positions it replaced. The original matrix is left "
      "unchanged, and an assertion in the script checks this. The function was also "
      "run on part of the toy matrix from the assignment sheet."),
    P("Program output (only part of the matrix is printed; all 8,753 rows would not fit):", h3),
    Preformatted(output.split("Trend population")[0].strip(), code),
    Spacer(1, 4),
    P("<b>Result:</b> 105 values were replaced, in 94 rows: 94 socioeconomic index "
      "values and 11 population values. No case counts were missing."),

    PageBreak(),
    P("Task 2: Plot the data", h2),
    *fig("plot1_cleaned.png", "Figure 1 (a). Cleaned data: every row, including the "
         "replaced ones."),
    *fig("plot2_highlighted.png", "Figure 2 (b). The 11 rows whose population was "
         "replaced by -1 are shown as red crosses at x = -1."),
    *fig("plot3_valid_only.png", "Figure 3 (c). Valid rows only: the 94 rows with any "
         "missing value are removed. A least-squares line is added."),
    *fig("plot4_index_vs_rate.png", "Figure 4 (extra). Socioeconomic index against "
         "cases per 10,000 people. Here the -1 placeholder sits on the x-axis as if it "
         "were a real index level."),

    P("Task 3: Describe the behaviour", h2),
    P("<b>(a) Trend.</b> Population and weekly cases show no clear relationship. "
      "Most groups report only 1&ndash;5 cases a week, whatever their size, and the "
      "fitted line is almost flat (slope = -4.2&times;10<super>-6</super>, r = "
      "-0.012; Figure 3). It is neither increasing nor decreasing, and not linear. "
      "The highest counts (up to 187) come from groups of 10,000&ndash;35,000 people."),
    P("<b>(b) Replaced values.</b> The 11 population placeholders lie at x = -1 "
      "(Figure 2). On a scale reaching 185,000 they blend in with the smallest real "
      "groups, so they look plausible. The "
      "socioeconomic placeholders stand out much more (Figure 4). They form an "
      "\"index -1\" column apart from levels 1&ndash;4, with rates about 10 per 10,000. "
      "The real levels have medians of 1&ndash;2 per 10,000."),
    P("<b>(c) Distortion.</b> -1 is treated as a real number. The mean "
      "socioeconomic index falls from 2.898 to 2.856. A trend line of rate against index "
      "would be pulled down by the high-rate cluster at -1 and suggest a steep, false "
      "pattern. A population of -1 also gives negative incidence rates, which make no "
      "sense. The population&ndash;cases line hardly changes (r = -0.009 against "
      "-0.012), only because 11 of the 8,753 rows are affected."),
    P("<b>(d) Alternatives.</b> Removing the affected rows costs only 94 rows (1.1%), "
      "so it is the safest choice here. Median imputation for population (13,602) keeps "
      "every row but invents values for groups whose size is truly unknown. For a "
      "categorical field such as the index, a separate \"unknown\" category is better than "
      "a number. A negative placeholder only suits formats that cannot store NaN, "
      "and must be filtered out before analysis."),

    PageBreak(),
    P("Appendix: Python code (assignment.py)", h2),
    Preformatted(source, code),
]

doc = SimpleDocTemplate(os.path.join(HERE, "report.pdf"), pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title="Cleaning and Visualising Data")
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print("report.pdf written")
