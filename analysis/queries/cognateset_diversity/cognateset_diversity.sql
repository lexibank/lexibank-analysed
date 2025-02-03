SELECT
    c.cldf_cognatesetReference AS CognateSet,
    p.concepticon_gloss AS Concept,
    CASE WHEN l.SubGroup = 'Tacana' THEN 'Tacana' ELSE 'Pano' END AS SubGroup,
    Count(DISTINCT(l.cldf_id)) AS Frequency
FROM
    CognateTable AS c,
    ParameterTable AS p,
    LanguageTable AS l,
    FormTable AS f
INNER JOIN
    (
        SELECT 
            COUNT(*) AS Count,
            new.CognateSet AS CognateSet
        FROM
            (
                SELECT DISTINCT
                    p2.concepticon_gloss as concepticon_gloss,
                    c2.cldf_cognatesetReference AS CognateSet
                FROM
                    ParameterTable AS p2,
                    CognateTable AS c2,
                    FormTable AS f2,
                    LanguageTable AS l2
                WHERE
                    f2.cldf_parameterReference = p2.cldf_id
                        AND
                    f2.cldf_id = c2.cldf_formReference
                        AND
                    f2.cldf_languageReference = l2.cldf_id
                        AND
                    l2.family = 'Pano-Tacanan'
            ) as new
        GROUP BY 
            CognateSet
        HAVING 
            COUNT(*) >= 5
        ORDER BY 
            Count DESC, CognateSet
    ) as freq
ON
    freq.CognateSet = c.cldf_cognatesetReference
WHERE
    f.cldf_parameterReference = p.cldf_id
        AND
    f.cldf_id = c.cldf_formReference
        AND
    f.cldf_languageReference = l.cldf_id
        AND
    l.family = 'Pano-Tacanan'
GROUP BY
    CognateSet, Concept, SubGroup