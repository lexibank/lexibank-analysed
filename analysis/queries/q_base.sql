WITH cc AS (
    SELECT
        l.cldf_id as Language_ID,
        l.cldf_glottocode as Glottocode,
        p.Concepticon_Gloss,
        p.Core_Concept,
        cc(f.Dolgo_Sound_Classes) as Consonant_Classes
    FROM
        LanguageTable as l,
        ParameterTable as p,
        FormTable as f
    WHERE
        l.cldf_id = f.cldf_languageReference AND
        p.cldf_id = f.cldf_parameterReference AND
        l.Selexion = 1
)
SELECT
    l.cldf_name,
    l.cldf_id,
    l.cldf_glottocode,
    l.Family,
    l.cldf_latitude,
    l.cldf_longitude,
    COUNT(DISTINCT selected_language.Concepticon_Gloss) AS Hits
FROM
(  -- Consonant classes for forms from the selected language.
    SELECT Concepticon_Gloss, Core_Concept, Consonant_Classes
    FROM cc
    WHERE Glottocode = ?
) AS selected_language
JOIN
(  -- Consonant classes for forms from other languages.
    SELECT Language_ID, Consonant_Classes, Concepticon_Gloss
    FROM cc
    WHERE Glottocode != ?
) AS other_languages
ON
    selected_language.Concepticon_Gloss = other_languages.Concepticon_Gloss
JOIN  -- We are interested in summary stats on language level.
    LanguageTable as l
ON
    other_languages.Language_ID = l.cldf_id
WHERE
    selected_language.Core_Concept like '%Tadmor-2009-100%' AND
    selected_language.Consonant_Classes = other_languages.Consonant_Classes
GROUP BY other_languages.Language_ID
HAVING Hits >= 3
ORDER BY Hits DESC;
