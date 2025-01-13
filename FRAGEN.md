# Infos/Anmerkungen/Fragen zu den Metadaten

## Projektkürzel
- Projektkürzel in den Metadaten? Wie sieht das bei Projekten aus wie bspw. bei *vase*, *qhod*?

## Datacite
- Datacite-Metadaten: als Datenstrom (`datacite.xml`)? Im Datacite sollen folgende Felder stehen:
    - Titel in englischer Sprache
    - Creator(s) + Orcid
    - Rechte
    - Contributor(s)
    - Contributor-Type
    - Issued-Date
    - Type (z.B. Text)
    - Language

## Elisabeths Wunschliste

**Digitales Objekt** (object.csv)
- Urheber/creator (bevorzugt eine natürliche Person)
- Rechte/rights (dropdown/URI)
- Titel (EN!)
- publisher: GAMS
- Description (bestenfalls optional, mMn ziemlich sinnfrei)
- object type: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#section-7
- lang (Liste der in den Datenströmen angegeben lang Werte)

**Datenströme/Dateien** (datastreams.csv)
- Urheber/creator (bevorzugt eine natürliche Person)
- Rechte/rights (dropdown/URI)
- mimetype (> geschlossene Liste von erlaubten Repo-Formaten, zb kein jpeg und normales pdf)
- size
- Titel (EN!)
- Description (bestenfalls optional, mMn ziemlich sinnfrei)
- bagpath
- (mMn kein publisher notwendig da am digitalen Objekt vorhanden, könnte weg)
- lang (Liste der erkannten Sprachen für Textdateien bzw. für Dateien, bei den eine Angabe der Sprache sinnvoll ist)

**Encoding**
- nur UTF-8 ist erlaubt, muss validiert werden!

**timestamps/audit trail**: handling durch repo nach aufnahme? publication date dort verpflichtend
  für Digitales Objekt und Datenströme

**Inhalt** (retro vs born digital! weil ein TEI zb bei retro zumindest zwei creator hat, den author und den editor...) (`DC.xml`)
- ID (entspricht PID bzw. recid)
- Titel (zumindest auch EN)
- Creator (bevorzugt eine natürliche Person)
- Rights (dropdown/URI)
- empfohlen natürlich viele Dinge (Datum, Ort, etc.)


**Liste für Default Titel (vorläufiger Entwurf)**
- Primär-XML: Titel XML = Titel DC (EN)
- DC: Dublin Core
- RDF: ? (RDF Statements?)
- METS: METS
- alle image mime types: Image (GAMS3 hat Facsimile, was ich nicht so gut finde)

Gunter: Für folgende Filenamen setzte ich  aktuell diese titles/descriptions:

```python
FILENAME_MAP = {
    "DC.xml": {
        "title": "Dublin Core Metadata",
        "description": "Dublin Core Metadata in XML format for this content file.",
    },
    "TEI.xml": {
        "title": "Main TEI file",
        "description": "The central TEI File for this object"
    },
    "LIDO.xml": {
        "title": "Main LIDO file",
        "description": "The central LIDO file of this object"
    },
    "RDF.xml": {
        "title": "RDF Statements",
        "description": ""
    }
}
``` 
Für die Bilder setzte ich "Image: {dsid}". Dasselbe für Audio und Video

**zu kären**: Woher kenne ich den Primär-Datenstrom?  Könnte das etwas sein, das im object.csv steht?

## Offene Fragen von Elisabeth
- an welchem Punkt werden die Handles vergeben
- wann/wo werden zusätzliche Metadatenformate erzeugt
- wann/wo die Suchindizierung
- wie wird versioniert
- wann/wie erfolgt die Übernahme von welchen Teilen ins Repo
- brauchen wir auch einen Thumbnail im bag? oder läuft das alles über IIIF?

## Berücksichtigte Aspekte bei den Metadaten zur Dokumentation (mit Hinblick LZA/FAIR)

**Allgemeines**

Es wird in Zukunft die Trennung zwischen Metadaten für das digitale Objekt und Metadaten für den Inhalt möglich. Ersteres wird durch .csv Dateien abgebildet (und/oder durch eine DataCite Datei), zweiteres durch ein DC.xml im Ordner des Objektes. Im DC steht daher in Zukunft nur mehr die Beschreibung des Inhalts! (Änderung zu jetzt)
überall sollte für jedes Metadatenfeld erkennbar sein, in welcher Sprache es befüllt ist. die Metadaten auf Ebene digitales Objekt und Datenströme sind verpflichtend auf Englisch anzugeben. im DC.xml muss zumindest der Titel auch auf Englisch vorhanden sein (entspricht im Normalfall eh dem Titel digitales Objekt)

**Minimalzitat nach Urheberrecht**

muss enthalten: title, creator, "Stelle" (=Link/PID). diese sollten also möglichst aussagekräftig sowohl für das digitale Objekt wie für den Datenstrom vorhanden sein (natürlich nicht schön bei Default-Datenstrom-Namen, aber der Link ist ja jeweils gegeben. aber da zumindest IMAGE 1 zB dazuschreiben, nicht nur Image?)

**Kompatibilität CSIP (https://earkcsip.dilcis.eu/)**

es muss erkennbar sein, ob es sich um SIP, AIP oder DIP handelt
irgendein Typ muss festgelegt werden, aber auf dem Niveau Text scheint ausreichend
leider bilden die in ihrer METS-Spezifikation mega kompliziert die physische Ordnerstruktur ab, die nicht unserer entspricht. keine weiterführende logische Struktur, was ich viel sinnvoller finden würde, finde ich unglücklich gelöst (weil die Ordnernamen und Struktur nicht expliziert sind sondern erst wieder implizit über die Spec festgelegt werden), siehe Bsp. oben

**Kompatibilität RDA Interoperability WG (http://dx.doi.org/10.15497/RDA00025)**

im Wesentlichen DataCite und die Ordnerstruktur bzw. das Bag

**InvenioRDM**

da InvenioRDM DataCite zur Metadatenverwaltung benutzt, die Vorgaben von DataCite
InvenioRDM verlangt in language ISO 639-3 (schlecht, da wir überall IANA codes erfassen)
zur Frage: ist der publisher die gams oder der herausgeber/projektleiter? invenio sagt defaults to name of the repo (Änderung zu jetzt)
Typisierung auf Basis des DCTerms Vokabulars

die Erstellung einer DataCite Datei zur Beschreibung des digitalen Objekts scheint daher eine sinnvolle Möglichkeit (bzw. sollten wir die entsprechenden Daten dafür haben). da würden dann Dinge wie ORCID, ROR, funder, grant ID etc. relevant werden.
die Infos, die pro Datenstrom/Datei verlangt werden, decken sich großteils.


## METS-Datenstrom
Elisabeth hat einen Beispiel-METS-Datenstrom erstellt, der als Template dienen könnte. Im METS sollte auch
die Beziehung der einzelnen Datenströme zueinander definiert werden. Das ist im folgenden METS (noch) nicht
ersichtlich?
```xml
<?xml version="1.0" encoding="UTF-8"?>
<mets:mets xmlns:csip="https://DILCIS.eu/XML/METS/CSIPExtensionMETS"
    xmlns:mets="http://www.loc.gov/METS/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xlink="http://www.w3.org/1999/xlink" OBJID="hsa.letter.1"
    LABEL="Charles Baissac an Hugo Schuchardt (15-00432)" TYPE="Text"
    PROFILE="https://earkcsip.dilcis.eu/profile/E-ARK-CSIP.xml"
    xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd http://www.w3.org/1999/xlink http://www.loc.gov/standards/mets/xlink.xsd https://DILCIS.eu/XML/METS/CSIPExtensionMETS https://earkcsip.dilcis.eu/schema/DILCISExtensionMETS.xsd">
    <mets:metsHdr CREATEDATE="2018-04-24T14:37:49.602+01:00"
        LASTMODDATE="2018-04-24T14:37:49.602+01:00" csip:OAISPACKAGETYPE="SIP">
        <!-- hier gibt es ein attribut RECORDSTATUS dass man für die unterscheidung von neu oder updaten nehmen könnte -->
        <mets:agent ROLE="CREATOR" TYPE="OTHER" OTHERTYPE="SOFTWARE">
            <mets:name>
               Fabio and Gunter's fancy packaging tool (FGFPT)
            </mets:name>
            <mets:note csip:NOTETYPE="SOFTWARE VERSION">
                1.0
            </mets:note>
        </mets:agent>
    </mets:metsHdr>
    <mets:dmdSec ID="DATACITE" CREATED="2018-04-24T14:37:49.609+01:00"><!-- würde hier  auf datacite.xml zeigen, wenn wir davon ausgehen, dass das package beschrieben wird -->
        <mets:mdRef LOCTYPE="URL" MDTYPE="OTHER" MDTYPEVERSION="2002" xlink:type="simple"
            xlink:href="metadata/datacite.xml" SIZE="903" MIMETYPE="text/xml"
            CREATED="2018-04-24T14:37:49.609+01:00"
            CHECKSUM="F24263BF09994749F335E1664DCE0086DB6DCA323FDB6996938BCD28EA9E8153"
            CHECKSUMTYPE="SHA-256"/><!-- man könnte hier noch mehr metadaten(dateien) haben, zb für die files/datenströme -->
    </mets:dmdSec>
    <mets:amdSec>
        <mets:rightsMD ID="RMD.1">
            <mets:mdWrap MDTYPE="OTHER" MIMETYPE="text/xml" OTHERMDTYPE="DVRIGHTS">
                <mets:xmlData><!-- ist nicht ganz klar, ob man da unbedingt mit mdRef auf eine andere datei muss -->
                    <oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/"
                        xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                        xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
                       <dc:creator>Urheber</dc:creator>
                        <dc:rights>https://creativecommons.org/licenses/by-nc/4.0</dc:rights>
                    </oai_dc:dc><!-- man könnte hier noch mehr metadaten(dateien) haben, zb für die files/datenströme -->
                </mets:xmlData>
            </mets:mdWrap>
        </mets:rightsMD>
     <!-- digiprovMD ist optional -->

    </mets:amdSec>
    <mets:fileSec><!-- attribut USE ist optional, könnten wir aber irgendwie sinnvoll verwenden -->
        <mets:fileGrp><!-- da gibt es in der specification ziemlich wilde vorgaben, was man haben muss (in der aufteilung nach ordnern documentation, schemas und representations). habe das mal ausgelassen und einfach unsere files gelistet -->
            <mets:file ID="DC" USE="METADATA"
                MIMETYPE="text/xml"
                SIZE="2554366" CREATED="2012-08-15T12:08:15.432+01:00"
                CHECKSUM="91B7A2C0A1614AA8F3DAF11DB4A1C981F14BAA25E6A0336F715B7C513E7A1557"
                CHECKSUMTYPE="SHA-256">
                <mets:FLocat LOCTYPE="URL" xlink:type="simple" xlink:href="data/content/DC.xml"
                />
            </mets:file>
            <mets:file ID="TEI" USE="TEXT" 
                MIMETYPE="text/xml"
                SIZE="2554366" CREATED="2012-08-15T12:08:15.432+01:00"
                CHECKSUM="91B7A2C0A1614AA8F3DAF11DB4A1C981F14BAA25E6A0336F715B7C513E7A1557"
                CHECKSUMTYPE="SHA-256">
                <mets:FLocat LOCTYPE="URL" xlink:type="simple" xlink:href="data/content/TEI_SOURCE.xml"
                />
            </mets:file>
            <mets:file ID="IMG.1" USE="FACSIMILE" MIMETYPE="image/jpeg" SIZE="123917"
                CREATED="2018-04-24T14:37:49.617+01:00"
                CHECKSUM="0BF9E16ADE296EF277C7B8E5D249D300F1E1EB59F2DCBD89644B676D66F72DCC"
                CHECKSUMTYPE="SHA-256">
                <mets:FLocat LOCTYPE="URL" xlink:type="simple" xlink:href="data/content/IMG.1.jpg"/>
            </mets:file>
        </mets:fileGrp>
       
    </mets:fileSec><!-- die structMap würde die ordnerstruktur (=physisch) und alle dateien in den ordnern zuweisen -->
    <mets:structMap ID="appdx1.struct-map-example-1" TYPE="PHYSICAL" LABEL="CSIP">
        <mets:div ID="appdx1.struct-map-example-div" LABEL="csip-mets-example">
            <mets:div ID="appdx1.struct-map-metadata-div" LABEL="Metadata"
                ADMID="appdx1.digiprov-premis-file-1 appdx1.digiprov-premis-file-2"
                DMDID="appdx1.dmd-ead-file"> </mets:div>
            <mets:div ID="appdx1.struct-map-doc-div" LABEL="Documentation">
                <mets:fptr FILEID="appdx1.file-grp-doc"> </mets:fptr>
            </mets:div>
            <mets:div ID="appdx1.struct-map-schema-div" LABEL="Schemas">
                <mets:fptr FILEID="appdx1.file-grp-schema"> </mets:fptr>
            </mets:div>
            <mets:div ID="appdx1.struct-map-reps-sub-div" LABEL="Representations">
                <mets:fptr FILEID="appdx1.file-grp-rep-subdata"> </mets:fptr>
            </mets:div>
        </mets:div>
    </mets:structMap>
</mets:mets>
```
