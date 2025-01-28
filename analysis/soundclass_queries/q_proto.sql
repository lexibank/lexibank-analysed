SELECT
    Language_Name,
    Language_ID,
    Glottocode,
    Family,
    Latitude,
    Longitude,
    COUNT(DISTINCT Concepticon_Gloss) as Hits
FROM
(
    SELECT
        t2.cldf_name as Language_Name,
        t2.cldf_id as Language_ID,
        t2.cldf_glottocode as Glottocode,
        t2.Family as Family,
        t2.cldf_latitude as Latitude,
        t2.cldf_longitude as Longitude,
        p1.Concepticon_Gloss as Concepticon_Gloss,
        f1.cldf_segments as Segments_A,
        t2.cldf_segments as Segments_B,
        CASE
            WHEN SUBSTR(f1.Dolgo_Sound_Classes, 1, 1) = 'V'
            THEN SUBSTR('H' || REPLACE(f1.Dolgo_Sound_Classes, 'V', '') || 'H', 0, 3)
            ELSE SUBSTR(REPLACE(f1.Dolgo_Sound_Classes, 'V', '') || 'H', 0, 3)
        END as Consonant_Classes_A,
        Consonant_Classes_B
    FROM
        --LanguageTable as l1,
        ParameterTable as p1,
        FormTable as f1
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
                THEN SUBSTR('H' || REPLACE(f2.Dolgo_Sound_Classes, 'V', '') || 'H', 0, 3)
                ELSE SUBSTR(REPLACE(f2.Dolgo_Sound_Classes, 'V', '') || 'H', 0, 3)
            END as Consonant_Classes_B
        FROM
            LanguageTable as l2,
            ParameterTable as p2,
            FormTable as f2
        WHERE
            l2.cldf_id = f2.cldf_languageReference AND
            p2.cldf_id = f2.cldf_parameterReference
    ) as t2
    ON
        p1.Concepticon_Gloss == t2.Concepticon_Gloss AND
        f1.cldf_languageReference != t2.cldf_id
    WHERE
        p1.Core_Concept like '%Swadesh-1955-100%' AND
        f1.cldf_languageReference == 'proto' AND
        -- f1.cldf_languageReference = l1.cldf_id AND
        p1.cldf_id == f1.cldf_parameterReference AND
        Consonant_Classes_A = Consonant_Classes_B
)
GROUP BY
    Language_Name,
    Language_ID,
    Glottocode
HAVING Hits >= 5
ORDER BY Hits DESC
;



