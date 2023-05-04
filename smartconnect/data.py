BLANK_DATAMODEL_CONTENT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<DataModel xmlns="http://www.smartconservationsoftware.org/xml/1.0/datamodel">
    <languages>
        <language code="en"/>
    </languages>
    <attributes>
        <attribute key="bright_ti4" isrequired="false" type="NUMERIC">
            <aggregations aggregation="avg"/>
            <aggregations aggregation="max"/>
            <aggregations aggregation="min"/>
            <aggregations aggregation="stddev_samp"/>
            <aggregations aggregation="sum"/>
            <aggregations aggregation="var_samp"/>
            <names language_code="en" value="Brightness ti4"/>
        </attribute>
        <attribute key="bright_ti5" isrequired="false" type="NUMERIC">
            <aggregations aggregation="avg"/>
            <aggregations aggregation="max"/>
            <aggregations aggregation="min"/>
            <aggregations aggregation="stddev_samp"/>
            <aggregations aggregation="sum"/>
            <aggregations aggregation="var_samp"/>
            <names language_code="en" value="Brightness ti5"/>
        </attribute>
        <attribute key="fireradiativepower" isrequired="false" type="TEXT">
            <qa_regex></qa_regex>
            <names language_code="en" value="Fire Radiative Power"/>
        </attribute>
        <attribute key="frp" isrequired="false" type="NUMERIC">
            <aggregations aggregation="avg"/>
            <aggregations aggregation="max"/>
            <aggregations aggregation="min"/>
            <aggregations aggregation="stddev_samp"/>
            <aggregations aggregation="sum"/>
            <aggregations aggregation="var_samp"/>
            <names language_code="en" value="Fire Radiative Power"/>
        </attribute>
        <attribute key="confidence" isrequired="false" type="NUMERIC">
            <aggregations aggregation="avg"/>
            <aggregations aggregation="max"/>
            <aggregations aggregation="min"/>
            <aggregations aggregation="stddev_samp"/>
            <aggregations aggregation="sum"/>
            <aggregations aggregation="var_samp"/>
            <names language_code="en" value="Confidence"/>
        </attribute>
        <attribute key="clustered_alerts" isrequired="false" type="NUMERIC">
            <aggregations aggregation="avg"/>
            <aggregations aggregation="max"/>
            <aggregations aggregation="min"/>
            <aggregations aggregation="stddev_samp"/>
            <aggregations aggregation="sum"/>
            <aggregations aggregation="var_samp"/>
            <names language_code="en" value="Clustered Alerts"/>
        </attribute>
    </attributes>
    <categories>
        <category key="gfwfirealert" ismultiple="true" isactive="true" iconkey="fire">
            <names language_code="en" value="GFW Fire Alert"/>
            <attribute isactive="true" attributekey="bright_ti4"/>
            <attribute isactive="true" attributekey="bright_ti5"/>
            <attribute isactive="true" attributekey="frp"/>
            <attribute isactive="true" attributekey="clustered_alerts"/>
        </category>
        <category key="gfwgladalert" ismultiple="true" isactive="true" iconkey="stump">
            <names language_code="en" value="GFW Glad Alert"/>
            <attribute isactive="true" attributekey="confidence"/>
        </category>
    </categories>
</DataModel>
"""

