import re
import logging

from lxml import html
from lxml.html.clean import Cleaner

from evaluator import evaluate_script
from css_adjustor import Adjustor
from tqdm import tqdm


def process(filename: str, ):
    logger = logging.getLogger()
    logger.info(f"Processing Given File: {filename}")
    tree = html.parse(filename)
    processor = Processor()
    processor.process(tree)
    return


class Processor:
    STYLE_PREFIX = "sheet-"
    p = re.compile('^<<.*>>$')

    def __init__(self,
                 input_filename: str = "input/sheet.html",
                 output_filename: str = "output/sheet.html",
                 output_css_filename: str = "output/style.css"):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.output_css_filename = output_css_filename
        self.logger = logging.getLogger()
        return

    def process(self, etree: html.etree):
        css_element = self.extract_CSS(etree)
        self.adjust_css_and_write(css_element)
        self.write_additional_styles(self.output_css_filename)

        html_processes = [
            self.cleanup_sheet_html,
            self.adjust_html_style_to_roll20,
            self.eval_cell_contents,
            self.clean_theads,
            self.write_html,
        ]
        for html_process in html_processes:
            etree = html_process(etree)

        return

    @staticmethod
    def extract_CSS(etree: html.etree):
        css_element: html.HtmlElement = etree.xpath("//style")[0]
        return css_element

    def adjust_css_and_write(self, css_element: html.HtmlElement):
        self.logger.info("Adjust and Write CSS file.")
        adjustor = Adjustor()
        stylesheet = adjustor.adjust_css_test(css_element.text_content())
        adjustor.write_file(stylesheet, self.output_css_filename)
        return

    def write_additional_styles(self, output_filename: str = "output/style.css") -> None:
        style_addons = ["input/google_style_roll20.css", "input/base_style.css"]

        self.logger.info(f"Write Additional styles into {output_filename}")
        with open(output_filename, "a", encoding="UTF-8") as f:
            for filename in tqdm(style_addons, "Writing additional styles"):
                f.write("\n")
                with open(filename, "r", encoding="UTF-8") as addons_f:
                    f.write(addons_f.read())
        return

    @staticmethod
    def cleanup_sheet_html(etree: html.etree):
        cleaner = Cleaner(scripts=True, javascript=True, inline_style=False, style=True,
                          comments=True, meta=True, annoying_tags=True,
                          remove_tags=["body"],
                          kill_tags=["svg"],
                          safe_attrs=(html.defs.safe_attrs | {'style'}))
        cleaned_tree: html.etree = cleaner.clean_html(etree)
        return cleaned_tree

    def clean_theads(self, etree: html.etree):
        for cell in tqdm(etree.xpath(f'//div/div/table/thead/tr/th'), desc="Cleaning Theads"):
            cell.text = ''
        for cell in tqdm(etree.xpath(f'//div/div/table/tbody/tr/th/div'), desc="Cleaning Ths"):
            cell.text = ''
        return etree

    def adjust_html_style_to_roll20(self, etree: html.etree):
        # tag: html.HtmlElement
        for tag in tqdm(etree.xpath(f'//*[contains(@class, "")]'), desc="Adjust html styles"):
            clazz_names = []
            for clazz in tag.classes:
                clazz_names.append(f"{clazz}")
                clazz_names.append(f"{self.STYLE_PREFIX}{clazz}")
            for clazz_name in clazz_names:
                tag.classes.toggle(clazz_name)
        return etree

    def eval_cell_contents(self, etree: html.etree):
        # cell: html.HtmlElement
        for cell in etree.xpath("//*"):
            if cell.text and self.is_script(cell.text):
                script = cell.text
                cell.text = ''
                cell.tail = ''
                cell.insert(0, evaluate_script(script))
        return etree

    def is_script(self, cell_content: str):
        if re.fullmatch(self.p, cell_content):
            return True
        return False

    @staticmethod
    def write_html(etree: html.etree):
        etree.write("output/sheet.html", encoding="UTF-8", pretty_print=True)
        return etree
