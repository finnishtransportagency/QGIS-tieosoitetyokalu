- Installation.
    1. Download the zip file from Github release.

    2. Open Qgis > Plugins > Manage and Install Plugins > Install from Zip > choose the downloaded zip file > press Install Plugin.

    3. Check if the plugin is installed and enabled: Manage and Install plugins > Installed.
    
- Description and usage.
    Osoitetyokalu plugin uses VKM-API to retrieve and display address information in various ways on the QGIS canvas. The plugin is split into five different tools. Address data in VKM-API is retrieved using HTTP GET-requests.

    1. Road address tool. A click tool that displays a road adress as annotation of the closest road in 15m radius from the clicked point on canvas.

    2. Search tool. Operates the same way as the first tool but in addition gives extra address information about the clicked point in a separate window.

    3. Road part tool. Highlights a road part's roadways and starting and ending points of a clicked road. Centers canvas to the ending point of the part.

    4. Starting and ending point -tool. Highlights roadways between two clicked points (A and B), adds annotations with road addresses to the clicked points and displays address information and length of the roadways on a separate window. Move the canvas with keyboard arrows after choosing the first point.

    5. Centering tool. Opens a search form with lines to input VKM-API request parameters. Once "Search" button is pressed, returns address information about a point or a line depending on the given search parameters and centers the canvas on the requested point.

    6. Delete tool. Opens a window with buttons to delete one or all annotations in the current project. Ability to delete layers and features will be added later.

- Extra.
    -Highlighted roadways are distinguished by their colors. 0 = green, 1 = yellow and 2 = blue. In the road part tool, green square marks the starting point and red is the ending point.

    -For stability, close all tool windows after you are done working with said tool.

    -Important!!! The more points and lines (=layers) there are on the canvas simultaneously the worse QGIS is performing. Delete or hide unneeded layers to improve performance using the field to the left of the canvas. Delete annotations through Delete tool.

    This is because each geometry is added as a seperate layer instead of adding them as features to existing layers which is the better solution. This will be fixed in the next version.