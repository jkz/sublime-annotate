import sublime, sublime_plugin

set = [
    'setup',
    'exceptional',
    'critical',
    'untested'
]

print("YES")

def region_to_json(region):
    return {'a': region.a, 'b': region.b}

def json_to_region(json):
    return sublime.Region(int(json['a']), int(json['b']))

class FoldMixin(object):
    def foldable_regions(self, regions):
        return sublime.Region(r.a - 1, r.b) for r in self.annotated_regions()

    def annotated_regions(self, tag):
        if tag:
            return region for region in view.get_regions(tag)
        else:
            return region for tag in tags for region in view.get_regions(tag)

    def fold(self, tag=None):
        self.winow().active_view().fold(list(self.foldable_regions()))

    def unfold(self, tag=None):
        self.winow().active_view().unfold(list(self.foldable_regions()))

class AnnotateCommandBase(sublime_plugin.WindowCommand):
    prompt = 'Annotate Tag:'

    def run(self, tag=None):
        view = self.window().active_view()
        if not view:
            return

        if tag:
            return self.on_done(tag)

        self.window.show_input_panel(self.prompt, "", self.on_done, None, None)

class AnnotateCommand(sublime_plugin.WindowCommand, AnnotateCommandBase):
    def on_done(self, tag):
        view = self.window.active_view()
        if not view:
            return

        tag = tag or 'default'
        tags.add(tag)

        settings = view.settings()
        scope = settings.get('annotate_scope_' + tag)
        regions = view.get_regions(tag)
        regions.extend(list(view.sel()))
        regions = [r for r in regions]
        view.add_regions(str(tag), regions, scope, 'dot', sublime.PERSISTENT | sublime.DRAW_OUTLINED)
        # view.add_regions(str(tag + '__fold'), fold_regions, '', 'cross', sublime.PERSISTENT | sublime.DRAW_EMPTY)
        highlight_origami(view)

class ClearAnnotationsCommand(AnnotateCommandBase):
    #TODO clear regions contained within selection
    def on_done(self, tag):
        view = self.window.active_view()
        if not view:
            return

        if tag:
            view.erase_regions(tag)
            tags.remove(tag)
        else:
            for tag in tags:
                view.erase_regions(tag)
                tags.remove(tag)

        highlight_origami(view)

class AnnotateListenerCommand(sublime_plugin.EventListener):
    def on_activated(self, view):
        highlight_origami(view)

    def on_post_save(self, view):
        # Store the current annotations to file
        pass

    def on_modified(self, view):
        # Update the annotations
        highlight_origami(view)

class FoldAnnotatedCommand(AnnotateCommandBase, FoldMixin):
    def on_done(self, tag):
        self.unfold(tag)

class UnfoldAnnotatedCommand(AnnotateCommandBase, FoldMixin):
    def on_done(self, tag):
        self.fold(tag)

class ToggleAnnotatedCommand(AnnotateCommandBase, FoldMixin):
    def on_done(self, tag):
        settings = self.window().active_view().settings()
        key = "annotate_fold_{}".format(tag)
        fold = settings.get(key, True):

        if fold:
            self.fold(tag)
        else:
            self.unfold(tag)

        settings.set(key, not fold)

