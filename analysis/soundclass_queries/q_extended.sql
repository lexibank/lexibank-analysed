WITH find_matches AS (
    SELECT
        Language_Name,
        Language_ID,
        Glottocode,
        Family,
        Latitude,
        Longitude,
        Concepticon_Gloss,
        Central_Concept,
        Consonant_Classes_A,
        Segments_A,
        Segments_B
    FROM
    (   SELECT
            t2.cldf_name as Language_Name,
            t2.cldf_id as Language_ID,
            t2.cldf_glottocode as Glottocode,
            t2.Family as Family,
            t2.cldf_latitude as Latitude,
            t2.cldf_longitude as Longitude,
            t1.Concepticon_Gloss as Concepticon_Gloss,
            t1.Central_Concept as Central_Concept,
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
                p1.Central_Concept as Central_Concept,
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
    )),
    grouped as (
        SELECT
            find_matches.Glottocode as Glottocode,
            COUNT(DISTINCT(find_matches.Concepticon_Gloss)) as Hits
        FROM
            find_matches
        GROUP BY Glottocode
        HAVING Hits >= 3
    )

-- This works if running exclusively
-- SELECT
--     find_matches.Language_Name as Language_Name,
--     find_matches.Glottocode as Glottocode,
--     find_matches.Family as Family,
--     find_matches.Latitude as Latitude,
--     find_matches.Longitude as Longitude,
--     find_matches.Concepticon_Gloss as Concepticon_Gloss,
--     find_matches.Central_Concept as Central_Concept,
--     find_matches.Consonant_Classes_A as Consonant_Classes_A,
--     find_matches.Segments_A as Segments_A,
--     find_matches.Segments_B as Segments_B
-- FROM find_matches
-- ORDER BY find_matches.Language_Name DESC

-- This works if running exclusively
-- SELECT
--     grouped.Glottocode,
--     grouped.Hits
-- FROM grouped
-- ORDER BY grouped.Hits DESC

-- But the join call seems to enter some recursive state (beca     use both glottocodes have the same origin, namely find_matches?)
SELECT
    find_matches.Language_Name as Language_Name,
    find_matches.Language_ID as Language_ID,
    find_matches.Glottocode as Glottocode,                              
    find_matches.Family as Family,
    find_matches.Latitude as Latitude,      
    find_matches.Longitude as Longitude,
    find_matches.Concepticon_Gloss as Concepticon_Gloss,
    find_matches.Central_Concept as Central_Concept,
    find_matches.Consonant_Classes_A as Consonant_Classes_A,
    find_matches.Segments_A as Segments_A,
    find_matches.Segments_B as Segments_B,
    grouped.Hits as Hits
FROM find_matches
JOIN grouped on find_matches.Glottocode = grouped.Glottocode
ORDER BY Hits DESC, Glottocode
;
