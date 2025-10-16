![Väyläviraston logo](https://vayla.fi/documents/25230764/35412219/vayla_sivussa_fi_sv_rgb.png)
# QGIS-tieosoitetyökalu

### Kuvaus
Tieosoitetyökalu-lisäosa mahdollistaa monipuoliset hakutoiminnot tie- ja katuosoitteella.
Saat tieosoitteen sekä muita tien ominaisuuksia näkyviin helposti karttaa klikkaamalla.
Voit myös tarkastella tieosia, hakea kohteita tieosoitevälillä sekä hakea sijainnin koordinaatilla.
Tieosoitevälin ajoratojen osoitetiedot saa talletettua tiedostona taulukkolaskentaohjelmiin viemiseksi.

**Documentation in English can be found below.**

**Syventävät ohjeet (PDF): https://ava.vaylapilvi.fi/ava/Muut/QGIS/QGIS-Tieosoitety%C3%B6kalu_Ohje.pdf**  
**Ohjevideo: https://www.youtube.com/watch?v=3UiOASUd2yA**

### Asennus
#### Asennus Githubin kautta
1. Lataa Tieosoitetyokalu.zip-tiedosto Githubista: https://github.com/finnishtransportagency/QGIS-tieosoitetyokalu/releases.
2. QGIS > Lisäosat > Hallitse ja asenna lisäosia > Asenna ZIP-tiedostosta > valitse ladattu ZIP-tiedosto > Asenna lisäosa.
3. Varmista, että Tieosoitetyökalu-plugin on asennettu ja käytössä: Hallitse ja asenna lisäosia > Asennettu.

#### Asennus QGIS-lisäosien listalta
1. QGIS > Lisäosat > Hallitse ja asenna lisäosia > Kaikki > Etsi Tieosoitetyökalu > Asenna lisäosa.
2. Varmista, että Tieosoitetyökalu-plugin on asennettu ja käytössä: Hallitse ja asenna lisäosia > Asennettu.

### Käyttö
Tieosoitetyökalu-lisäosa hakee VKM-rajapinnasta osoitetietoja ja esittää niitä erilaisin tavoin QGIS:sissa. Data haetaan HTTP GET-pyyntöjen avulla JSON-muodossa.
Kartalle lisättyjä geometrioita(=feature) ja tasoja voi piilottaa/poistaa Qgissin vasemmasta kentästä, jossa jokanen taso löytyy omasta työkaluryhmästään.
Tieosoitetyökalu on jaettu kuuteen työkaluun, ja ne löytyvät dropdown-menusta QGIS:n yläpalkista.

1. Tieosoitetyökalu. Käynnistää klikkaus-työkalun, joka hakee käyttäjän karttaan tekemän klikkauksen perusteella lähimmän tien tieosoitteen 50 metrin säteellä.
Käyttäjän klikkaus palauttaa XY-koordinaatit, joita käytetään VKM-haussa. Tieosoitetyökalu kerää rajapinnan palautetusta datasta tien XY-koordinaatit ja osoitteen, jonka se sijoittaa karttavihjeenä kartalle käyttäen uusia koordinaatteja. Mikäli klikkauksen säteellä ei ole tieosoitteellisia pisteitä, VKM-rajapinta palauttaa virheen, joka esitetään kanvaksen yläreunassa. Tämä pätee myös muihin työkaluihin, jotka hyödyntävät hiiren painiketta.

2. Hakutyökalu. Toimii samalla tavalla kuin tieosoitetyökalu, mutta esittää myös mm. klikatun pisteen kunta- ja katuosoitteet, urakka-alueen, ELY-keskuksen nimen sekä m_arvon. Data esitetään erillisessä ikkunassa.

3. Tieosatyökalu. Korostaa klikatun tieosan mahdolliset ajoradat sekä alku- ja loppupisteet. Esittää tieosan alku- ja loppuosoitteen sekä pituuden karttavihjeen avulla ja kohdistaa ruudun tieosan puoleenväliin.

**Tieosoitetyökalun avulla korostetut ajoradat erotellaan värien perusteella: 0 = vihreä, 1 = punainen ja 2 = sininen.**

4. "Alku- ja loppupiste" -työkalu. Korostaa kahden (A ja B) klikatun pisteen väliset ajoradat ja esittää niiden alku- ja loppuosoitteet sekä pituudet erillisessä ikkunassa. Pisteiden on oltava samalla tiellä. Kun ensimmäinen piste on valittu, karttaa pitkin voi tarvittaessa siirtyä eri suuntiin käyttäen nuolinäppäimiä ennen toista klikkausta!!!

Viivamaisen haun pituus näytetään erikseen Ajoradat-ikkunan 'Tieputuus'-kentässä.
Haetun välin ajoratapätkien tiedot voi ladata CSV-tiedostoon, joka ilmestyy valittuun kansioon kolmea pistettä (...) ja 'Lataa..' painikkeita painamalla!

5. Kohdistustyökalu. Avaa tekstikenttiä sisältävän ikkunan, johon käyttäjä voi syöttää parametreja VKM-hakua varten. Palauttaa pisteen tai ajoratojen osoitetiedot, kohdistaa niihin ja lisää ne kartalle riippuen annetuista hakuparametreista.

6. Poistotyökalu. Poistaa yhden tai kaikki karttavihjeet ja myös yhden satunnaisen tai kaikki geometriat työkalun tasoista riippuen käyttäjän valinnasta.

**Tasot voi poistaa käyttäen QGIS-sovelluksen vasemmassa reunassa olevaa tasopaneelia. Käyttäjä voi poistaa/piilottaa joko Tieosoitetyökalun pääryhmän tai valitsemansa työkaluryhmän tasot.**

#### Asetukset
Käyttäjä voi tarvittaessa määrittää välityspalvelimen ("proxy server") HTTP- ja/tai HTTPS-osoitteet QGIS-tieosoitetyökalun asetuksissa.

[EN]:
### Description
With Tieosoitetyökalu or Road address tool you can perform different kind of searches with road and street addresses.
This plugin displays road addresses and other address properties after a click on a canvas.
You can also examine road parts, highlight roadways between two chosen points and search locations by coordinates.
Address information of the highlighted roadway lines can be downloaded in a CSV file that is spreadsheet-friendly.

**Advanced instructions (PDF): https://ava.vaylapilvi.fi/ava/Muut/QGIS/QGIS-Tieosoitety%C3%B6kalu_Ohje.pdf**  
**Instructional video: https://www.youtube.com/watch?v=3UiOASUd2yA**

### Installation
#### Installation using Github
1. Download the Tieosoitetyokalu.zip file from Github release: https://github.com/finnishtransportagency/QGIS-tieosoitetyokalu/releases.
2. Open QGIS > Plugins > Manage and Install Plugins > Install from Zip > choose the downloaded zip file > press Install Plugin.
3. Check if the plugin is installed and enabled: Manage and Install plugins > Installed.

#### Installation from QGIS plugin repository
1. QGIS > Plugins > Manage and Install Plugins > All > Find Tieosoitetyökalu > Install Plugin.
2. Check if the plugin is installed and enabled: Manage and Install plugins > Installed.

### Usage
Tieosoitetyökalu plugin uses VKM-API to retrieve and display address information in various ways on the QGIS canvas. Address data in VKM-API is retrieved using HTTP GET-requests. You can hide added geometries (features) by using Qgis app's left side field where layers are placed in their respective tool groups.
Plugin's tools can be found in a drop-down menu above the canvas.

The plugin is split into six different tools:

1. Road address tool. A click tool that displays a road adress as an annotation of the closest road in 50m radius from the clicked point on canvas.

2. Search tool. Operates the same way as the first tool but in addition gives extra address information about the clicked point in a separate window.

3. Road part tool. Highlights a road part's roadways and starting and ending points of a clicked road. Adds an annotation with road address information and centers canvas to the halfway of the road part.

**Roadways highlighted by the plugin are distinguished by color: 0 = green, 1 = red ja 2 = blue.**

4. Starting and ending point -tool. Highlights roadways between two clicked points (A and B), adds annotations with road addresses to the clicked points and displays address information and length of the roadways on a separate window. You can move the canvas with keyboard arrows after choosing the first point!

Length between the two points is shown in a 'Road length' text field.
Starting and ending address data of every line of every road way retrieved from the linestring VKM-request can be downloaded as a CSV to a chosen folder by pressing buttons (...) and then 'Download..'!

5. Centering tool. Opens a search form with lines to input VKM-API request parameters. Once "Search" button is pressed, returns address information about a point or a line depending on the given search parameters and centers the canvas on the requested point.

6. Delete tool. Opens a window with buttons to delete one or all annotations in the current project. Also can delete one random geometry or all geometries that were added using this plugin.

**Layers can be deleted by choosing and deleting Tieosoitetyökalu plugin's main group or one of its subgroups that can be found in QGIS's layer panel.**

#### Settings
Proxy server HTTP and/or HTTPS addresses can be configured in Tieosoitetyökalu plugin's settings.

