SELECT
    Language_Name,
    Language_ID,
    Glottocode,
    Family,
    Latitude,
    Longitude,
    COUNT(DISTINCT Concepticon_Gloss) as Hits
FROM
(   SELECT
        t2.cldf_name as Language_Name,
        t2.cldf_id as Language_ID,
        t2.cldf_glottocode as Glottocode,
        t2.Family as Family,
        t2.cldf_latitude as Latitude,
        t2.cldf_longitude as Longitude,
        t1.Concepticon_Gloss as Concepticon_Gloss,
        t1.cldf_segments as Segments_A,
        t2.cldf_segments as Segments_B,
        t1.filter as selected_gcode,
        CASE
            WHEN SUBSTR(t1.Dolgo_Sound_Classes, 1, 1) = 'V'
            THEN SUBSTR('H' || REPLACE(REPLACE(REPLACE(t1.Dolgo_Sound_Classes, 'V', ''), '+', ''), '1', '') || 'H', 1, 2)
            ELSE SUBSTR(REPLACE(REPLACE(REPLACE(t1.Dolgo_Sound_Classes, 'V', ''), '+', ''), '1', '') || 'H', 1, 2)
        END as Consonant_Classes_A,
        Consonant_Classes_B
    FROM
        (SELECT
            p1.Concepticon_Gloss as Concepticon_Gloss,
            f1.cldf_segments as cldf_segments,
            f1.Dolgo_Sound_Classes as Dolgo_Sound_Classes,
            p1.Core_Concept as Core_Concept,
            p1.cldf_id as cldf_id,
            f1.cldf_languageReference as cldf_languageReference,
            f1.cldf_parameterReference as cldf_parameterReference,
            l1.filter as filter
        FROM
            LanguageTable as l1,
            ParameterTable as p1,
            FormTable as f1
        WHERE 
            l1.cldf_id = f1.cldf_languageReference AND
            p1.cldf_id = f1.cldf_parameterReference AND
            l1.cldf_glottocode = l1.filter
        ) as t1
    JOIN
    (
        SELECT
            l2.cldf_name,
            l2.cldf_id,
            l2.cldf_glottocode,
	        l2.Family,
	        l2.cldf_latitude,
	        l2.cldf_longitude,
            p2.Concepticon_Gloss,
            p2.cldf_name,
            f2.cldf_segments,
	        p2.Core_Concept,
            CASE
                WHEN SUBSTR(f2.Dolgo_Sound_Classes, 1, 1) = 'V'
                THEN SUBSTR('H' || REPLACE(REPLACE(REPLACE(f2.Dolgo_Sound_Classes, 'V', ''), '+', ''), '1', '') || 'H', 1, 2)
                ELSE SUBSTR(REPLACE(REPLACE(REPLACE(f2.Dolgo_Sound_Classes, 'V', ''), '+', ''), '1', '') || 'H', 1, 2)
            END as Consonant_Classes_B
        FROM
            LanguageTable as l2,
            ParameterTable as p2,
            FormTable as f2
        WHERE
            l2.cldf_id = f2.cldf_languageReference AND
            p2.cldf_id = f2.cldf_parameterReference AND
            l2.Selexion = 1
    ) as t2
    ON
        t1.Concepticon_Gloss == t2.Concepticon_Gloss AND
        t1.cldf_languageReference != t2.cldf_id
    WHERE
        t1.Core_Concept like '%Tadmor-2009-100%'
            AND
        t1.cldf_id == t1.cldf_parameterReference
            AND
        Consonant_Classes_A = Consonant_Classes_B
            AND
        t2.cldf_glottocode != selected_gcode
)
GROUP BY Glottocode
HAVING Hits >= 3
ORDER BY Hits DESC
;
