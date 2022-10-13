- Asennus. 
	1. Lataa Osoitetyokalu.zip-tiedosto Githubista.
	
	2. QGIS > Hallitse ja asenna lisäosia > Asenna ZIP-tiedostosta > valitse ladattu ZIP-tiedosto > Asenna lisäosa.
	
	3. Varmista, että Osoitetyökalu-plugin on asennettu ja käytössä: Hallitse ja asenna lisäosia > Asennettu.

- Käyttö.
	Osoitetyökalu-plugin hakee VKM-rajapinnasta osoitetietoja ja esittää niitä erilaisin tavoin QGIS:sissa. Data haetaan HTTP GET-pyyntöjen avulla JSON-muodossa.
	Kartalle lisättyjä geometrioita (feature) voi piilottaa Qgissin vasemmasta kentästä, jossa jokanen taso löytyy omasta työkaluryhmästään.
	Pluginin työkalut löytyvät dropdown-menusta Qgis:sin yläpalkista.

	Osoitetyökalu-plugin on jaettu kuuteen työkaluun:

	1. 	Tieosoitetyökalu. Käynnistää klikkaus-työkalun, joka hakee käyttäjän kanvakselle tekemän klikkauksen perusteella lähimmän tien tieosoitteen 15 metrin säteellä.
		Käyttäjän klikkaus palauttaa XY-koordinaatit, joita käytetään VKM-haussa. Tieosoitetyökalu kerää rajapinnan palautetusta datasta tien XY-koordinaatit ja osoitteen, 
		jonka se sijoittaa karttavihjeenä kanvakselle käyttäen uusia koordinaatteja.
	
		Mikäli klikkauksen säteellä ei ole tieosoitteellisia pisteitä, VKM-rajapinta palauttaa virheen, joka esitetään kanvaksen yläreunassa. Tämä pätee myös muihin työkaluihin, jotka hyödyntävät hiiren painiketta.
	
	2. 	Hakutyökalu. Toimii samalla tavalla kuin tieosoitetyökalu, mutta esittää myös mm. klikatun pisteen kunta- ja katuosoitteet sekä m_arvon. 
		Data esitetään erillisessä 	ikkunassa.
	
	3. 	Tieosatyökalu. Korostaa klikatun tieosan mahdolliset ajoradat sekä alku- ja loppupisteet. Esittää tieosan alku- ja loppuosoitteen sekä pituuden karttavihjeen avulla ja
		kohdistaa ruudun tieosan puoleenväliin.
	
	4. 	"Alku- ja loppupiste" -työkalu. Korostaa kahden (A ja B) klikatun pisteen väliset ajoradat ja esittää niiden alku- ja loppuosoitteet sekä pituudet erillisessä ikkunassa.
		Pisteiden on oltava samalla tiellä. Kun ensimmäinen piste on valittu, karttaa pitkin voi tarvittaessa siirtyä eri suuntiin käyttäen nuolinäppäimiä ennen toista klikkausta!!!
		
		Viivamaisen haun pituus näytetään erikseen Ajoradat-ikkunan 'Tieputuus'-kentässä.
		
		Haetun välin ajoratapätkien tiedot voi ladata CSV-tiedostoon, joka ilmestyy valittuun kansioon kolmea pistettä (...) ja 'Lataa..' painikkeita klikkaamalla!
	
	5.	Kohdistustyökalu. Avaa tekstikenttiä sisältävän ikkunan, johon käyttäjä voi syöttää parametreja VKM-hakua varten. Palauttaa pisteen tai ajoratojen osoitetiedot, 
		kohdistaa niihin ja lisää ne kartalle riippuen annetuista hakuparametreista.

		Viivamaisen haun pituus näytetään erikseen Ajoradat-ikkunan 'Tieputuus'-kentässä.
		
		Haetun välin ajoratapätkien tiedot voi ladata CSV-tiedostoon, joka ilmestyy valittuun kansioon kolmea pistettä (...) ja 'Lataa..' painikkeita klikkaamalla!
		
	6. 	Poistotyökalu. Poistaa yhden tai kaikki karttavihjeet ja myös yhden satunnaisen tai kaikki geometriat työkalun tasoista riippuen käyttäjän valinnasta. 
		Karttavihjeet kannattaa poistaa ainoastaan tämän työkalun avulla, muuten ne tulee takaisin esille uuden karttavihjeen tullessa kartalle. 
	
- Huom!
	-Korostetut ajoradat erotetaan värin avulla. 0 = vihreä, 1 = punainen, 2 = sininen.
	
	-Karttavihjeet kannattaa poistaa ainoastaan poistotyökalun kautta.



- Installation.
    1. Download the Osoitetyokalu.zip file from Github release.

    2. Open Qgis > Plugins > Manage and Install Plugins > Install from Zip > choose the downloaded zip file > press Install Plugin.

    3. Check if the plugin is installed and enabled: Manage and Install plugins > Installed.
    
- Description and usage.
    Osoitetyokalu plugin uses VKM-API to retrieve and display address information in various ways on the QGIS canvas. Address data in VKM-API is retrieved using HTTP GET-requests.
	You can hide added geometries (features) by using Qgis app's left side field where layers are placed in their respective tool groups.
	Plugin's tools can be found in a drop-down menu above the canvas.

	The plugin is split into six different tools:

    1. Road address tool. A click tool that displays a road adress as annotation of the closest road in 15m radius from the clicked point on canvas.

    2. Search tool. Operates the same way as the first tool but in addition gives extra address information about the clicked point in a separate window.

    3. Road part tool. Highlights a road part's roadways and starting and ending points of a clicked road. Adds an annotation with road address information and centers canvas to the halfway of the road part.

    4. Starting and ending point -tool. Highlights roadways between two clicked points (A and B), adds annotations with road addresses to the clicked points and displays address information and length of the roadways on a separate window. Move the canvas with keyboard arrows after choosing the first point.

	Length between the two points is shown in a 'Tiepituus' text field.

    Starting and ending address data of every line of every road way retrieved from the linestring VKM-request can be downloaded as a CSV to a chosen folder by pressing buttons (...) and 'Lataa..'!

    5. Centering tool. Opens a search form with lines to input VKM-API request parameters. Once "Search" button is pressed, returns address information about a point or a line depending on the given search parameters and centers the canvas on the requested point.

	Length between the two points is shown in a 'Tiepituus' text field.

    Starting and ending address data of every line of every road way retrieved from the linestring VKM-request can be downloaded as a CSV to a chosen folder by pressing buttons (...) and 'Lataa..'!

    6. Delete tool. Opens a window with buttons to delete one or all annotations in the current project. Also can delete one random geometry or all geometries that were added using this plugin.

- Extra!
    -Highlighted roadways are distinguished by their colors. 0 = green, 1 = red and 2 = blue. In the road part tool, green square marks the starting point and red is the ending point.

    -For stability, close all tool windows after you are done working with said tool.

    -Important!!! Delete annotations through Delete tool.