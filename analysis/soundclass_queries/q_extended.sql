WITH cc AS (
    SELECT
        l.cldf_id as Language_ID,
        l.cldf_glottocode as Glottocode,
        p.Concepticon_Gloss,
        p.Central_Concept,
        p.Core_Concept,
        f.cldf_segments,
        cc(f.Dolgo_Sound_Classes) as Consonant_Classes
    FROM
        LanguageTable as l,
        ParameterTable as p,
        FormTable as f
    WHERE
        l.cldf_id = f.cldf_languageReference AND
        p.cldf_id = f.cldf_parameterReference AND
        l.Selexion = 1
),
matches AS (
    SELECT
        t2.Language_ID,
        t1.Concepticon_Gloss,
        t1.Central_Concept as Central_Concept,
        t1.Consonant_Classes,
        t1.cldf_segments as Segments_A,
        t2.cldf_segments as Segments_B
    FROM
    (
        SELECT
            Concepticon_Gloss,
            cldf_segments,
            Consonant_Classes,
            Central_Concept
        FROM cc
        WHERE Glottocode = ? AND Core_Concept like '%Tadmor-2009-100%'
    ) as t1
    JOIN
    (
        SELECT
            Language_ID,
            Concepticon_Gloss,
            cldf_segments,
            Consonant_Classes
        FROM cc
        WHERE Glottocode != ?
    ) as t2
    ON t1.Concepticon_Gloss == t2.Concepticon_Gloss
    WHERE t1.Consonant_Classes = t2.Consonant_Classes
),
grouped_matches as (
    SELECT
        matches.Language_ID,
        COUNT(DISTINCT(matches.Concepticon_Gloss)) as Hits
    FROM matches
    GROUP BY matches.Language_ID
    HAVING Hits >= 3
)
SELECT
    l.cldf_name as Language_Name,
    l.cldf_id as Language_ID,
    l.cldf_glottocode as Glottocode,
    l.Family as Family,
    l.cldf_latitude as Latitude,
    l.cldf_longitude as Longitude,
    matches.Concepticon_Gloss,
    matches.Central_Concept,
    matches.Consonant_Classes,
    matches.Segments_A,
    matches.Segments_B,
    grouped_matches.Hits
FROM matches
JOIN grouped_matches on matches.Language_ID = grouped_matches.Language_ID
JOIN LanguageTable AS l ON matches.Language_ID = cldf_id
ORDER BY Hits DESC, Glottocode;
