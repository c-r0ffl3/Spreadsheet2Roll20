import cssutils
import logging
from tqdm import tqdm

cssutils.log.setLevel(logging.CRITICAL)


class Adjustor:
    def __init__(self,
                 css_prefix: str = "sheet-",
                 docs_font_prefix: str = "docs-"):
        self.CSS_PREFIX: str = css_prefix
        self.DOCS_FONT_PREFIX: str = docs_font_prefix
        self.logger = logging.getLogger(__name__)
        return

    def adjust_and_write(self,
                         input_filename: str = "input/style.css",
                         output_filename: str = "output/style.css"):
        style_sheet = self.adjust_css_file(input_filename)
        self.write_file(style_sheet, output_filename)
        return

    def adjust_css_text(self, style_text: str):
        sheet: cssutils.css.CSSStyleSheet = cssutils.parseString(style_text)
        return self.adjust(sheet)

    def adjust_css_file(self, input_filename: str = "input/style.css"):
        sheet: cssutils.css.CSSStyleSheet = cssutils.parseFile(input_filename)
        return self.adjust(sheet)

    def adjust(self,
               style_sheet: cssutils.css.CSSStyleSheet) -> cssutils.css.CSSStyleSheet:
        adjust_processes = [
            self.add_class_prefix,
            self.remove_font_prefix,
        ]
        for callable_adjust in adjust_processes:
            style_sheet = callable_adjust(style_sheet)
        return style_sheet

    def add_class_prefix(self,
                         style_sheet: cssutils.css.CSSStyleSheet) -> cssutils.css.CSSStyleSheet:
        for rule in tqdm(style_sheet, desc="Adjust CSS class names"):
            if rule.type == rule.STYLE_RULE:
                for selector in rule.selectorList:
                    selector.selectorText = selector.selectorText.replace(".", f".{self.CSS_PREFIX}")
        return style_sheet

    def remove_font_prefix(self,
                           style_sheet: cssutils.css.CSSStyleSheet) -> cssutils.css.CSSStyleSheet:
        style_sheet.add(
            """@import url(https://fonts.googleapis.com/css?kit=jv8BDwW_JDYjDnfsc4GHz3qw0PXvDLJkHTiJnIRN8B_RCVyl16ls4cZf6706XCk4V_kEOV_bGcReW78jQuQGCiuGx5YtTc_BoRewTdcf00M_lX1CboQY1OcWUtKtwaoiieLenizyHuC9-C0bkROLXABz5sPXLBhgNcOHdBf3ltn3rGVtsTkPsbDajuO5ueQw);""")
        for rule in tqdm(style_sheet, desc="Adjust CSS font styles"):
            if rule.type == rule.STYLE_RULE:
                for property in rule.style:
                    if property.name == "font-family":
                        property.value = property.value.replace(self.DOCS_FONT_PREFIX, '')
        return style_sheet

    def write_file(self, style_sheet: cssutils.css.CSSStyleSheet,
                   output_filename: str = "output/style.css") -> None:
        self.logger.debug(f"Writing file to . . . {output_filename}")
        with open(output_filename, "wb") as f:
            f.write(style_sheet.cssText)
        return


if __name__ == '__main__':
    adjustor = Adjustor()
    adjustor.adjust_and_write()
