from django.forms.widgets import RadioSelect, RadioFieldRenderer, mark_safe, force_unicode

class RadioFieldHorizontalRenderer(RadioFieldRenderer):
    """
    An object used by RadioSelect to enable customization of radio widgets.
    """

    def render(self):
        """Outputs a <table> for this set of radio fields."""
        
        return mark_safe(u'<table><tr>\n%s\n</tr></table>' % u'\n'.join([u'<td>%s</td>'
                % force_unicode(w) for w in self]))

class HorizontalRadioSelect( RadioSelect ):
    """
    Try to maake a radio select which produces horizintal options.
    """
    renderer = RadioFieldHorizontalRenderer