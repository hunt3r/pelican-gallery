#Pelican-Gallery: A Gallery plugin for the Pelican static site generator

This plugin creates a gallery attribute on content (article.gallery) you want to create.  You 
will define named presets which can be referenced in your templates.  It will attempt to be smart
about regenerating photos once they exist.  

- Resizes images respective of aspect ratio
- Allows for multiple presets e.g. -> article.gallery.photos[0]['thumb']

## Installation

Add gallery.py to your plugins folder.  You may need to set this up if you haven't already:
```
#Pelican Conf
PLUGIN_PATH = "my_plugins"
PLUGINS = [my_plugins.gallery"]
```
see: http://docs.getpelican.com/en/latest/plugins.html for more details on plugins in Pelican

This plugin requires the PIL library to function. Install Python PIL library in your virtual environment.  On Mac OSX I found that this works best if you use brew package manager as many of the underlying C libraries are easier to install using this method.  There are ways to do it without brew but you'll need to read up on what is best for your environment

```brew install pil```

Feel free to write more transforms, see the PIL docs for what it can do:
http://www.pythonware.com/media/data/pil-handbook.pdf 
http://effbot.org/imagingbook/image.htm
http://effbot.org/imagingbook/imageops.htm

##Settings:
You will need to add some variables to your pelicanconf.py and publishconf.py respectively.  The settings should be added towards the bottom as there are some dependencies on other variables that come with a basic pelican setup.  

###Example configuration values from peliconconf.py:
```
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
```

## Add to markdown header
```
Gallery: my/gallery/path
```

##Template implementation
This is just a sample of how you might iterate over a gallery in a template or template partial.

```
{% if article.gallery %}
    <h3>Gallery</h3>
    <ul class="thumbnails">
    {% for photo_set in article.gallery.photos %}
      <li class="{{THUMBNAIL_GALLERY_CLASS}}">
        <a href="{{ SITEURL }}/{{ photo_set['large'].src }}" class="thumbnail fancybox-thumbs" rel="article.gallery.galleryName">
          <img src="{{ SITEURL }}/{{ photo_set['thumb'].src }}" alt="{{ photo_set['thumb'].src }}" width="{{ photo_set['thumb'].width }}" height="{{ photo_set['thumb'].height }}" />
        </a>
      </li>
      {% endfor %}
    </ul>
{% endif %}
```

The MIT License (MIT)

Copyright (c) 2013 Christopher D. Hunter - chrishunters.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
