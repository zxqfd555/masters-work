from collections import deque
from html.parser import HTMLParser


class DOMNode:
    DUMMY_TEXT_NODE = object()

    def __init__(self, tag_name, node_attrs, parent=None, content=None):
        self._tag_name = tag_name
        self._node_attrs = node_attrs
        self._parent = parent

        self._children = []
        self._own_content_length = 0
        self._cached_content_length = 0
        self._content = content

    def add_content(self, content):
        actual_length = 0
        for c in content:
            if c not in (' ', '\n', '\r', '\t'):
                actual_length += 1

        if self._tag_name == 'a':
            actual_length = 0  # ignore hyperlink text

        self._children.append(DOMNode(self.DUMMY_TEXT_NODE, {}, self, content))
        self._own_content_length += actual_length

    def add_child(self, son):
        self._children.append(son)

    def get_tag_name(self):
        return self._tag_name

    def get_own_content_length(self):
        return self._own_content_length

    def get_content_length(self):
        self._cached_content_length = (
            self.get_own_content_length() + sum([child.get_content_length() for child in self._children])
        )
        return self._cached_content_length

    def get_cached_content_length(self):
        return self._cached_content_length

    def get_children(self):
        return self._children

    def serialize_to_html(self):
        if self._tag_name is self.DUMMY_TEXT_NODE:
            return self._content

        tag_start = '<{} {}>'.format(
            self._tag_name,
            ' '.join(['{}={}'.format(k, v) for k, v in self._node_attrs.items()])
        )
        tag_end = '</{}>'.format(self._tag_name)
        children_representations = ' '.join([child.serialize_to_html() for child in self._children])

        if self._parent and self._tag_name:
            return tag_start + children_representations + tag_end
        else:
            return children_representations


class GenericPageProcessor(HTMLParser):

    MAIN_BODY_TEXT_RATE = 0.30
    DESCENDANT_HAS_MAIN_BODY_CONTENT_RATE = 0.70

    BANNED_TAGS = [
            'script',
            'style',
            'iframe',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._root = DOMNode('', {})
        self._path_from_root = deque([self._root])
        self._is_fed_already = False

        self._links = set()

        self._title = None
        self._is_processing_title = False

    def handle_starttag(self, tag, attrs):
        attrs = self._attrs_to_dict(attrs)

        if tag == 'a' and 'href' in attrs:
            self._links.add(attrs['href'])
        elif tag == 'title':
            self._is_processing_title = True

        current_dom_node = DOMNode(tag, attrs, self._path_from_root[-1])
        self._path_from_root[-1].add_child(current_dom_node)
        self._path_from_root.append(current_dom_node)

    def handle_endtag(self, tag):
        if tag == 'title':
            self._is_processing_title = False

        self._path_from_root.pop()

    def handle_data(self, data):
        if self._is_processing_title:
            self._title = data

        if self._path_from_root[-1].get_tag_name().lower() in self.BANNED_TAGS:
            return

        self._path_from_root[-1].add_content(data)

    def feed(self, *args, **kwargs):
        if self._is_fed_already:
            raise RuntimeError('Feed cant be used more than once in GenericPageProcessor')

        super().feed(*args, **kwargs)

        self._is_fed_already = True

    def get_title(self):
        return self._title

    def get_links(self):
        return self._links

    def get_main_body(self):
        self._total_content_length = self._root.get_content_length()
        main_body_node = self._get_main_node(
            self._root,
            self._total_content_length * self.MAIN_BODY_TEXT_RATE,
            self.DESCENDANT_HAS_MAIN_BODY_CONTENT_RATE,
        )

        return main_body_node.serialize_to_html()

    def _get_main_node(self, node, min_content_len, max_split_rate):
        min_child_content_size = max(node.get_cached_content_length() * max_split_rate, min_content_len)
        for child in node.get_children():
            if child.get_cached_content_length() >= min_child_content_size:
                return self._get_main_node(child, min_content_len, max_split_rate)

        return node

    def _attrs_to_dict(self, attrs):
        result = {}
        for k, v in attrs:
            result[k] = v
        return result
