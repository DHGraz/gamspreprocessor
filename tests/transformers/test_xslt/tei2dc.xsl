<?xml version="1.0" encoding="UTF-8"?>
<!-- 
    Projectei: GAMS Projekttemplate
    Company: ZIM-ACDH (Zentrum Informationsmodellierung - Austrian Centre for Digital Humanities)
 -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:oai="http://www.openarchives.org/OAI/2.0/"
    exclude-result-prefixes="#all">
    
    <xsl:output method="xml" encoding="UTF-8"/>
    
    <xsl:param name="host" select="'https://gams.uni-graz.at/'"/>
    
    <xsl:variable name="teifile" select="tei:TEI/tei:teiHeader/tei:fileDesc"/>
    <xsl:variable name="teiencode" select="tei:TEI/tei:teiHeader/tei:encodingDesc"/>
    <xsl:variable name="teiprofile" select="tei:TEI/tei:teiHeader/tei:profileDesc"/>
    <xsl:variable name="pid-tei" select="$teifile/tei:publicationStmt/tei:idno"/>
    <xsl:variable name="rels-ext" select="concat($host, $pid-tei, '/RELS-EXT')"/>
   
    
    <xsl:variable name="creators"
        select="$teifile/tei:seriesStmt/tei:respStmt[@ana = 'marcrelator:pdr']/tei:persName"/>
    <!-- <xsl:variable name="creatorsforename" select="$teifile/tei:seriesStmt/tei:respStmt[@corresp='marcrelator:pdr']/tei:persName/tei:forename"/>
    <xsl:variable name="creatorssurname" select="$teifile/tei:seriesStmt/tei:respStmt[@corresp='marcrelator:pdr']/tei:persName/tei:surname"/><!-\- Projektleiter -\->
    -->
    
    <xsl:variable name="filetitle" select="$teifile/tei:titleStmt/tei:title"/>
    <!-- file title -->
    <xsl:variable name="projtitle" select="$teifile/tei:seriesStmt/tei:title"/>
    <!-- projekt title -->
    
    <xsl:variable name="publisher">
        <xsl:value-of select="$teifile/tei:publicationStmt/tei:publisher/tei:orgName"/>
    </xsl:variable>
   
    
    <xsl:variable name="pubyear"
        select="$teifile/tei:publicationStmt/tei:date[@ana = 'dcterms:issued']"/>
    
    <xsl:variable name="origdate"
        select="$teifile/tei:sourceDesc/tei:bibl/tei:date[@ana = 'dcterms:created']"/>
    
    <xsl:variable name="subjects"
        select="$teiprofile/tei:textClass/tei:keywords[@ana = 'subjects']/tei:list/tei:item"/>
    
    <xsl:variable name="contributors"
        select="$teifile/tei:seriesStmt/tei:respStmt[@ana = 'marcrelator:rth' or @ana = 'marcrelator:rtm' or @ana = 'marcrelator:res']/tei:persName"/>
    <!-- nicht projektleiter sondern zim mitarbeiter -->
    <!-- <xsl:variable name="contributorsforename" select="$teifile/tei:seriesStmt/tei:respStmt[@corresp='marcrelator:rth' or @corresp='marcrelator:rtm']/tei:persName/tei:forename"/>
    <xsl:variable name="contributorssurname" select="$teifile/tei:seriesStmt/tei:respStmt[@corresp='marcrelator:rth' or @corresp='marcrelator:rtm']/tei:persName/tei:surname"/>
   -->
    
    <xsl:variable name="languages" select="$teiprofile/tei:langUsage/tei:language/@ident"/>
    
    <!-- relatedidentifier -->
    <xsl:variable name="project" select="$teifile/tei:seriesStmt/tei:title"/>
    <!-- mit oder ohne 'context:' am ende darf context NICHT drin stehen -->
    <xsl:variable name="project-url" select="$teifile/tei:seriesStmt/tei:title/@ref"/>
    
    <xsl:variable name="rights" select="$teifile/tei:publicationStmt/tei:availability/tei:licence"/>
    <xsl:variable name="rights-url"
        select="$teifile/tei:publicationStmt/tei:availability/tei:licence/@target"/>
    
   
    
    <xsl:variable name="location"
        select="$teifile/tei:sourceDesc/tei:bibl/tei:placeName[@ana = 'marcrelator:prp']"/>
    <xsl:variable name="funderorgname"
        select="$teifile/tei:titleStmt/tei:funder[@ana = 'marcrelator:fnd']/tei:orgName"/>
    <xsl:variable name="fundernr"
        select="$teifile/tei:titleStmt/tei:funder[@ana = 'marcrelator:fnd']/tei:num"/>
    <xsl:variable name="fundername"
        select="$teifile/tei:titleStmt/tei:funder[@ana = 'marcrelator:fnd']/tei:name"/>
    
    <!-- <xsl:variable name="source" select=""/>
    <xsl:variable name="type" select=""/>
    <xsl:variable name="relation" select=""/>
    <xsl:variable name="format" select=""/>

    <xsl:variable name="coverage" select=""/>
   -->
    <xsl:template match="/">
        <oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
            <!-- Titel des Datensatzes -->
            <dc:title>   <xsl:value-of select="$filetitle"/></dc:title>
           
            <xsl:if test="$projtitle">
            <!-- Projekttitel; Achtung: Muss als erste dc:relation angegeben werden -->
            <dc:relation><xsl:value-of select="$projtitle"/></dc:relation>
            <!-- Link zur Projektseite,  ohne context!!!! -->
            <dc:relation><xsl:value-of select="$project-url"/></dc:relation>
            </xsl:if>
           
            <!-- Creator(s), in diesem Fall die Ersteller des Datensatzes -->
            <!-- Nachname, Vorname -->
            <xsl:if test="$creators"> 
               <xsl:for-each select="$creators">
                <dc:creator><xsl:value-of select="./tei:surname"/><xsl:text>, </xsl:text><xsl:value-of select="./tei:forename"/></dc:creator>
            </xsl:for-each>
            </xsl:if>
           
           
           <!-- objekt beschreibung hardcoden  -->
            <dc:description>this TEI file....</dc:description>
            
            
            <xsl:if test="$publisher">
                <dc:publisher><xsl:value-of select="$publisher"/></dc:publisher>
            </xsl:if>
           
            <xsl:if test="$contributors">
            <xsl:for-each select="$contributors"> 
                <dc:contributor><xsl:value-of select="./tei:surname"/><xsl:text>, </xsl:text><xsl:value-of select="./tei:forename"/>
                    </dc:contributor>
            </xsl:for-each>
            </xsl:if>
           
            <!-- im contributor auch den funder -->
            <xsl:if test="$funderorgname">
            <dc:contributor><xsl:value-of select="$funderorgname"/><xsl:text>, </xsl:text><xsl:value-of select="$fundernr"/></dc:contributor>
           </xsl:if>
            
            <!-- Mehrere Datumsangaben möglich. 
        Die erste Angabe sollte grundsätzlich das Datum der Erstellung der Ressource enthalten und wird im 
        Zitiervorschlag für das Publikationsjahr herangezogen. -->
            <xsl:if test="$pubyear">
                <dc:date><xsl:value-of select="$pubyear"/></dc:date>
            </xsl:if>
           
            <xsl:if test="$origdate">
                <dc:date><xsl:value-of select="$origdate"/></dc:date>
            </xsl:if>
           
            <!-- hardcoden -->
            <dc:format>tei+xml</dc:format>
            
            
            
            <!-- Gams Permalink -->
            <dc:identifier> <xsl:value-of select="$pid-tei"/></dc:identifier>
            
            <!-- anpassen -->
            <dc:source>Bib<!--selbstausfüllen wenn vorhanden--></dc:source>
            
            <xsl:if test="$languages">
                <dc:language><xsl:value-of select="$languages"/></dc:language></xsl:if>
            <xsl:if test="$location">
                <dc:coverage><xsl:value-of select="$location"/></dc:coverage></xsl:if>
          
            <xsl:if test="$rights">
                <!-- Menschenlesbare Rechteangabe, wird unter "License" ausgegeben -->
            <dc:rights><xsl:value-of select="$rights"/></dc:rights>
            <!-- Maschinenlesbarer Verweis auf Lizenz, unterlegt prosaisches dc:rights -->
            <dc:rights><xsl:value-of select="$rights-url"/></dc:rights>
            </xsl:if>
        </oai_dc:dc>
        
          </xsl:template>
    
</xsl:stylesheet>

