from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    PageChooserPanel,
    StreamFieldPanel)
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from wagtailio.features.blocks import FeatureIndexPageBlock
from wagtailio.utils.models import (
    SocialMediaMixin,
    CrossPageMixin,
)


class Bullet(Orderable, models.Model):
    snippet = ParentalKey('features.FeatureAspect', related_name='bullets')
    title = models.CharField(max_length=255)
    text = RichTextField()

    panels = [
        FieldPanel('title'),
        FieldPanel('text')
    ]


@register_snippet
class FeatureAspect(ClusterableModel):
    title = models.CharField(max_length=255)
    screenshot = models.ForeignKey(
        'images.WagtailIOImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def __str__(self):
        return self.title

    panels = [
        FieldPanel('title'),
        InlinePanel('bullets', label="Bullets"),
        ImageChooserPanel('screenshot')
    ]


class FeatureDescriptionFeatureAspect(Orderable, models.Model):
    page = ParentalKey('features.FeatureDescription', related_name='feature_aspects')
    feature_aspect = models.ForeignKey('features.FeatureAspect', related_name='+')

    panels = [
        SnippetChooserPanel('feature_aspect')
    ]


@register_snippet
class FeatureDescription(ClusterableModel):
    title = models.CharField(max_length=255)
    introduction = models.CharField(max_length=255, blank=True)
    documentation_link = models.URLField(max_length=255, blank=True)

    def __str__(self):
        return self.title

    panels = [
        FieldPanel('title'),
        FieldPanel('introduction'),
        FieldPanel('documentation_link'),
        InlinePanel('feature_aspects', label="Feature Aspects"),
    ]


class FeaturePageFeatureAspect(Orderable, models.Model):
    page = ParentalKey('features.FeaturePage', related_name='feature_aspects')
    feature_aspect = models.ForeignKey(
        'features.FeatureAspect',
        related_name='+'
    )

    panels = [
        SnippetChooserPanel('feature_aspect')
    ]


class FeaturePage(Page, SocialMediaMixin, CrossPageMixin):
    introduction = models.CharField(max_length=255)

    @property
    def feature_index(self):
        return FeatureIndexPage.objects.ancestor_of(
            self
        ).order_by('-depth').first()

    @property
    def previous(self):
        if self.get_prev_sibling():
            return self.get_prev_sibling()
        else:
            return self.get_siblings().last()

    @property
    def next(self):
        if self.get_next_sibling():
            return self.get_next_sibling()
        else:
            return self.get_siblings().first()

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        InlinePanel('feature_aspects', label="Feature Aspects")
    ]

    promote_panels = Page.promote_panels + SocialMediaMixin.panels + \
        CrossPageMixin.panels


class FeatureIndexPageMenuOption(models.Model):
    page = ParentalKey('features.FeatureIndexPage',
                       related_name='secondary_menu_options')
    link = models.ForeignKey(
        'wagtailcore.Page',
        related_name='+'
    )
    label = models.CharField(max_length=255)

    panels = [
        PageChooserPanel('link'),
        FieldPanel('label')
    ]


class FeatureIndexPage(Page):
    # TODO: Remove the introduction field, when body streamfield is ready
    introduction = models.CharField(max_length=255)
    body = StreamField(FeatureIndexPageBlock())

    @property
    def features(self):
        return FeaturePage.objects.live().child_of(self)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),

        # TODO: Remove the following fields, when body streamfield is ready
        # FieldPanel('introduction'),
        # InlinePanel('secondary_menu_options', label="Secondary Menu Options")
    ]
