import logging, json, os, sys, time
from pelican import signals
from PIL import ImageOps, Image

"""

Gallery plugin for Pelican
==========================

This plugin creates a gallery attribute on content (article.gallery) you want to create.  You
will define named presets which can be referenced in your templates.  It will attempt to be smart
about regenerating photos once they exist.

- Resizes images respective of aspect ratio
- Allows for multiple presets e.g. -> article.gallery.photos[0]['thumb']

Settings:
---------

Example configuration:

GALLERY_FOLDER = "galleries"
GALLERY_SRC_PATH = "%s%s" % (BASE_PATH, "gallery_src")
GALLERY_OUTPUT_PATH = "%s%s%s" % (BASE_PATH, OUTPUT_PATH, GALLERY_FOLDER)
GALLERY_REGENERATE_EXISTING = False
GALLERY_PRESETS = [
                    {"name": "thumb", "actions": [{"type": "fit", "height": 100, "width": 100, "from": (0.5, 0.5) }]},
                    {"name": "slider", "actions": [{"type": "fit", "height": 300, "width": 900, "from": (0.5, 0.5) }]},
                    {"name": "large", "actions": [{"type": "resize", "height": 640, "width": 850, "from": (0.5, 0.5) }]},
                    {"name": "thumb_greyscale",
                        "actions": [
                            {"type": "fit", "height": 100, "width": 100, "from": (0.5, 0.5) },
                            {"type": "greyscale"}
                        ]},
                  ]

# This setting is optional, used for thumbnails in bootstrap
THUMBNAIL_GALLERY_CLASS = "span2"

Article metadata example:
-------------------------
Gallery: <Relative path from GALLERY_SRC_PATH>

{% if article.gallery %}
    <h3>Gallery</h3>
    <ul class="thumbnails">
    {% for photo_set in article.gallery.photos %}
      <li class="{{THUMBNAIL_GALLERY_CLASS}}">
        <a href="{{ SITEURL }}/{{ photo_set['large'].src }}" class="thumbnail fancybox-thumbs" rel="article.gallery.galleryName">
          <img src="{{ SITEURL }}/{{ photo_set['thumb'].src }}" alt="{{ photo_set['thumb'].src }}" />
        </a>
      </li>
      {% endfor %}
    </ul>
{% endif %}

"""


class Photo():

    """ Class to represent a Photo, also handles applying presets to itself"""
    def __init__(self, gallery, filename, output_path, preset):
        self.gallery = gallery
        self.filename = filename
        self.input_file = "%s%s%s" % (self.gallery.absolute_src_path, os.sep, self.filename)
        self.output_path = output_path
        self.output_file = "%s%s%s" % (output_path, os.sep, self.filename)
        self.preset = preset
        self.image = None
        self.width = None
        self.height = None
        self.image = Image.open(self.input_file)
        self.process_image()
        self.image = Image.open(self.output_file)
        self.width, self.height = self.image.size
        self.src = "%s%s%s%s%s%s%s" %(self.gallery.generator.settings["GALLERY_FOLDER"],
                                        os.sep,
                                        self.gallery.gallery_name,
                                        os.sep,
                                        self.preset["name"],
                                        os.sep,
                                        self.filename)

    def process_image(self):
        """Responsible for applying presets to the Image obj"""
        if not os.path.isfile(self.output_file) or self.gallery.generator.settings["GALLERY_REGENERATE_EXISTING"]:

            # Actions should be processed in order of appearance in actions array
            for i in range(len(self.preset["actions"])):
                a = self.preset["actions"][i]

                if a["type"] == "fit":
                    if not "from" in a:
                        a["from"] = (0.5, 0.5) # crop from middle by default

                    self.image = ImageOps.fit(self.image, (a["width"], a["height"],), method=Image.ANTIALIAS, centering=a["from"])

                if a["type"] == "greyscale":
                    self.image = ImageOps.grayscale(self.image)

                if a["type"] == "resize":
                    self.image.thumbnail((a["width"], a["height"]), Image.NEAREST)

                # TODO: Write other useful transforms here!

            self.image.save(self.output_file, "JPEG")


class Gallery():
    """Represents a Gallery, iterate of gallery.photos in your Template"""
    def __init__(self, generator, metadata):
        self.generator = generator
        self.gallery_name = None
        self.files = []
        self.photos = []
        self.absolute_src_path = None
        self.absolute_output_path = None
        self.metadata = metadata
        self.preset_dir = []

        if "gallery" in self.metadata:
            self.gallery_name = self.metadata["gallery"]
            self.absolute_src_path =  "%s%s%s" % (self.generator.settings["GALLERY_SRC_PATH"],
                                                    os.sep,
                                                    self.gallery_name)

            self.absolute_output_path = "%s%s%s" % (self.generator.settings["GALLERY_OUTPUT_PATH"],
                                                    os.sep,
                                                    self.gallery_name)

            self.create_preset_folders()
            self.create_preset_images()

    def create_preset_images(self):
        """Creates the image assets for each preset and returns a PhotoSet object"""
        for f in sorted(self.get_files_from_data()):
            photoInstances = {}
            for preset in self.generator.settings["GALLERY_PRESETS"]:
                preset_dir = "%s%s%s" % (self.absolute_output_path,
                                         os.sep,
                                         preset["name"])
                photoInstances[preset["name"]] = Photo(self, f, preset_dir, preset)

            self.photos.append(photoInstances)

    def create_preset_folders(self):
        """Creates the folder structure for a gallery"""

        if not os.path.exists(self.absolute_output_path):
            os.makedirs(self.absolute_output_path)

        # Create gallery preset folders for this gallery
        if "GALLERY_PRESETS" in self.generator.settings:
            for preset in self.generator.settings["GALLERY_PRESETS"]:
                preset_dir = "%s%s%s" % (self.absolute_output_path,
                                        os.sep,
                                        preset["name"])
                self.preset_dir.append(preset_dir)
                if not os.path.exists(preset_dir):
                    os.makedirs(preset_dir)
        else:
            print("You have no presets defined, please add GALLERY_PRESETS array to settings file, with at least one preset defined, see docs.")

    def get_files_from_data(self):
        print("getting files for %s" % self.absolute_src_path)
        from os import listdir
        from os.path import isfile, join
        return [ f for f in listdir(self.absolute_src_path) if isfile(join(self.absolute_src_path,f)) and f != ".DS_Store" ]


def get_galleries(generator, metadata):
    if "gallery" in metadata.keys():
        metadata["gallery"] = Gallery(generator, metadata)

def register():
    # signals.article_generator_init.connect(init_gallery_plugin)
    signals.article_generator_context.connect(get_galleries)
    signals.page_generator_context.connect(get_galleries)

