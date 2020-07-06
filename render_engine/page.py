import logging

import re
import typing
from typing import List
from pathlib import Path

from jinja2 import Markup
from markdown import markdown

from ._type_hint_helpers import PathString

#some attributes will need to be protected from manipulation

# default matching param for posts
base_matcher = re.compile(r"(^\w+: \b.+$)", flags=re.M)


def parse_content(content: str, matcher=base_matcher):
    """
    split content into attributes and content text

    Parameters:
        content : str
            The content to be parsed
        matcher : str, optional
            A compiled regular expression that splits the content.
            default `base_matcher`
    """

    parsed_content = re.split(matcher, content)
    content = parsed_content.pop().strip()

    attrs = list(filter(lambda x: x.strip(), parsed_content))
    return attrs, content


class Page:
    """
    Base component used to make web pages.

    All components that represent content in HTML, XML, or JSON generated by 
    Render Engine should be a Page object.

    Pages can be rendered directly from a template or from a file.

    Page objects can be used to extend existing page objects.


    Examples:
        ```
        # Basic Page with No Template Variables
        @site.register_route('basic_page.html')
        class BasicPage(Page):
            template = 'template_file.html' # user provided template

        # Basic Page with Variables
        @site.register_route('page_with_vars')
        class PageWithVars(Page):
            title = 'Site Title'

        # Page Loading from File
        @site.register_route('page_from_file')
        class PageFromFile(Page):
            content_path = 'index.md' # loaded from content path can be '.md' or '.html'

        # Page Inherited from Other Page
        @site.register_route('basic_page.html')
        class BasicPage(Page):
            template = 'template_file.html' # user provided template
            title = 'Base Page'

        @site.register_route('other_page.html')
        class InheritingPage(Page):
            # template will be inherited from the BasicPage
            title = 'Inherited Page'
        ```

    Attributes:
        engine: str, optional
            The engine that the Site should refer to or the site's default engine
        template: str
            The template that the Site should refer to. If empty, use site's default
        routes: List[str]
            all routes that the file should be created at. default []
        content_path: List[PathString], optional
            the filepath to load content from.
        slug: str
            The engine's default route filename
        content: str
            preprocessed text stripped from initialized content. This will not
            include any defined attrs
        html: str
            text converted to html from _content
    """

    engine = ""
    template = ""
    routes = [""]
    list_attrs = ['tags']

    def __init__(
        self,
        content_path: PathString = None,
        content: str = "",
        matcher=base_matcher,
        no_index: bool = False,
    ):
        """
        If a content_path exists, check the associated file, processing the
        vars at the top and restitching the remaining lines

        Parameters:
            content_path: List[PathString], optional
                the filepath to load content from.
            content: str, optional
                raw text to be processed into HTML
            matcher: str, optional
                A compiled regular expression that splits the content.
                defatul `base_matcher`

        TODOs:
            - ADD Documentation for attrs/content
            - Make Slug Conversion Smarter

        """

        self.no_index = no_index

        if hasattr(self, 'content_path'):
            content = Path(self.content_path).read_text()

        elif content_path:
            content = Path(content_path).read_text()

        valid_attrs, self._content = parse_content(content, matcher=matcher)


        for attr in valid_attrs:
            name, value = attr.split(": ", maxsplit=1)

            # comma delimit attributes.
            if name.lower() in self.list_attrs:
                value = list(map(lambda x:x.lower(), value.split(', ')))

            else:
                value = value.strip()

            setattr(self, name.lower(), value)

        if not hasattr(self, 'title'):
            self.title = getattr(self, 'name', None) or self.__class__.__name__

        if not hasattr(self, "slug"):
            self.slug = getattr(self, "title", self.__class__.__name__)

        _slug = self.slug.lower().replace(" ", "_")
        self.slug = re.sub(r'[!\[\]\(\)]', '', _slug)

        logging.debug(f'{self.title}, {self.content}')

        self.url = f'{self.routes[0]}/{self.slug}'

    def __str__(self):
        return self.slug

    @property
    def html(self):
        """Text from self._content converted to html"""
        return markdown(self._content)


    @property
    def content(self):
        """html = rendered html (not marked up). Is `None` if `content == None`"""
        if self._content:
            return Markup(self.html)

        else:
            return ""
