- Asennus. 
	1. Lataa ZIP-tiedosto Githubista.
	
	2. QGIS > Hallitse ja asenna lisäosia > Asenna ZIP-tiedostosta > valitse ladattu ZIP-tiedosto > Asenna lisäosa.
	
	3. Varmista, että Osoitetyökalu-plugin on asennettu ja käytössä: Hallitse ja asenna lisäosia > Asennettu.

- Käyttö.
	Osoitetyökalu-plugin hakee VKM-rajapinnasta osoitetietoja ja esittää niitä erilaisin tavoin QGIS:sissa. Data haetaan HTTP GET-pyyntöjen avulla JSON-muodossa.
	Se on jaettu kuuteen työkaluun:

	1. 	Tieosoitetyökalu. Käynnistää klikkaus-työkalun, joka hakee käyttäjän kanvakselle tekemän klikkauksen perusteella lähimmän tien tieosoitteen 15 metrin säteellä.
		Käyttäjän klikkaus palauttaa XY-koordinaatit, joita käytetään VKM-haussa. Tieosoitetyökalu kerää rajapinnan palautetusta datasta tien XY-koordinaatit ja osoitteen, 
		jonka se sijoittaa karttavihjeenä kanvakselle käyttäen uusia koordinaatteja.
	
		Mikäli klikkauksen säteellä ei ole tieosoitteellisia pisteitä, VKM-rajapinta palauttaa virheen, joka esitetään kanvaksen yläreunassa. Tämä pätee myös muihin työkaluihin, jotka hyödyntävät hiiren painiketta.
	
	2. 	Hakutyökalu. Toimii samalla tavalla kuin tieosoitetyökalu, mutta esittää myös mm. klikatun pisteen kunta- ja katuosoitteet sekä m_arvon. Data esitetään erillisessä ikkunassa.
	
	3. 	Tieosatyökalu. Korostaa klikatun tieosan mahdolliset ajoradat sekä alku- ja loppupisteet. Esittää tieosan alku- ja loppuosoitteen sekä pituuden karttavihjeen avulla, joka pisteiden väliin.
	
	4. 	"Alku- ja loppupiste" -työkalu. Korostaa kahden (A ja B) klikatun pisteen väliset ajoradat ja esittää niiden alku- ja loppuosoitteet sekä pituudet erillisessä ikkunassa.
		Pisteiden on oltava samalla tiellä. Kun ensimmäinen piste on valittu, karttaa pitkin voi tarvittaessa siirtyä eri suuntiin käyttäen nuolinäppäimiä ennen toista klikkausta!!!
		
		Haetun välin ajoratapätkien tiedot voi ladata CSV-tiedostoon, joka ilmestyy valittuun kansioon!
	
	5.	Kohdistustyökalu. Avaa tekstikenttiä sisältävän ikkunan, johon käyttäjä voi syöttää parametreja VKM-hakua varten. Palauttaa pisteen tai ajoratojen osoitetiedot, kohdistaa niihin 
		ja lisää ne kanvakselle riippuen annetuista hakuparametreista.
		
		Haetun välin ajoratapätkien tiedot voi ladata CSV-tiedostoon, joka ilmestyy valittuun kansioon!
		
	6. 	Poistotyökalu. Poistaa yhden tai kaikki karttavihjeet riippuen käyttäjän valinnasta. Karttavihjeet kannattaa poistaa ainoastaan tämän työkalun avulla, 
		muuten ne tulee takaisin esille uuden karttavihjeen tullessa kartalle.
	
- Huom!
	-Korostetut ajoradat erotetaan värin avulla. 0 = vihreä, 1 = keltainen, 2 = sininen.
	
	-!!!Mitä enemmän pisteitä ja viivoja (=tasoja) on yhtäaikaisesti kanvaksella, sitä hitaammin QGIS pyörii!!! Turhia tasoja kannattaa poistaa tai piilottaa käyttäen vasemassa laidassa sijaitsevaa kenttää, jonka avulla voi poistaa tai piilottaa valitut tasot. Karttavihjeet kannattaa poistaa ainoastaan poistotyökalun kautta.



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

    Starting and ending address data of every line of every road way retrieved from the linestring VKM-request can be downloaded as a CSV!

    5. Centering tool. Opens a search form with lines to input VKM-API request parameters. Once "Search" button is pressed, returns address information about a point or a line depending on the given search parameters and centers the canvas on the requested point.

    Starting and ending address data of every line of every road way retrieved from the linestring VKM-request can be downloaded as a CSV!

    6. Delete tool. Opens a window with buttons to delete one or all annotations in the current project. Ability to delete layers and features will be added later.

- Extra!
    -Highlighted roadways are distinguished by their colors. 0 = green, 1 = yellow and 2 = blue. In the road part tool, green square marks the starting point and red is the ending point.

    -For stability, close all tool windows after you are done working with said tool.

    -Important!!! The more points and lines (=layers) there are on the canvas simultaneously the worse QGIS is performing. Delete or hide unneeded layers to improve performance using the field to the left of the canvas. Delete annotations through Delete tool.

    This is because each geometry is added as a seperate layer instead of adding them as features to existing layers which is the better solution. This will be fixed in the next version.