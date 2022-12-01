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


OUTPUT_SHEET_PATH = "sheet.html"
OUTPUT_CSS_PATH = "style.css"


class Processor:
    STYLE_PREFIX = "sheet-"
    SCRIPT_PATTERN = re.compile('^<<.*>>$')

    def __init__(self,
                 input_filename: str = "input/sheet.html",
                 output_filename: str = OUTPUT_SHEET_PATH,
                 output_css_filename: str = OUTPUT_CSS_PATH):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.output_css_filename = output_css_filename
        self.logger = logging.getLogger()
        return

    def process(self, etree: html.etree):
        self.process_css(etree)
        self.process_html(etree)
        return

    def process_css(self, etree: html.etree):
        self.logger.info(f"Process CSS . . .")
        css_element = self.extract_css_from(etree)
        self.adjust_css_and_write(css_element)
        self.write_additional_styles(self.output_css_filename)
        return

    def extract_css_from(self, etree: html.etree):
        self.logger.info(f"Extract CSS from given file: {self.input_filename}")
        css_element: html.HtmlElement = etree.xpath("//style")[0]
        return css_element

    def adjust_css_and_write(self, css_element: html.HtmlElement):
        self.logger.info("Adjust CSS")
        adjustor = Adjustor()
        stylesheet = adjustor.adjust_css_text(css_element.text_content())
        self.logger.info(f"Write files into: {self.output_css_filename}")
        adjustor.write_file(stylesheet, self.output_css_filename)
        return

    def write_additional_styles(self) -> None:
        style_addons = ["input/google_style_roll20.css", "input/base_style.css"]

        self.logger.info(f"Write Additional styles into {self.output_filename}")
        with open(self.output_filename, "a", encoding="UTF-8") as f:
            for filename in tqdm(style_addons, "Writing additional styles"):
                f.write("\n")
                with open(filename, "r", encoding="UTF-8") as addons_f:
                    f.write(addons_f.read())
        return

    def process_html(self, etree: html.etree) -> None:
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

    def cleanup_sheet_html(self, etree: html.etree):
        self.logger.info(f"Clean up the given HTML file: {self.input_filename}")
        cleaner = Cleaner(scripts=True, javascript=True, inline_style=False, style=True,
                          comments=True, meta=True, annoying_tags=True,
                          remove_tags=["body"],
                          kill_tags=["svg"],
                          safe_attrs=(html.defs.safe_attrs | {'style'}))
        cleaned_tree: html.etree = cleaner.clean_html(etree)
        return cleaned_tree

    def clean_theads(self, etree: html.etree):
        self.logger.info(f"Remove unnecessary tags")
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
        if re.fullmatch(self.SCRIPT_PATTERN, cell_content):
            return True
        return False

    def write_html(self, etree: html.etree):
        self.logger.info(f"Write files into: {self.output_filename}")
        etree.write(self.output_filename, encoding="UTF-8", pretty_print=True)
        return etree
