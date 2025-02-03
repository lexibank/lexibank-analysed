SELECT 
    COUNT(DISTINCT(p.concepticon_gloss)) AS Count,
    l.cldf_name AS Doculect,
    l.cldf_glottocode AS Glottocode,
    l.family AS Family,
    l.cldf_latitude,
    l.cldf_longitude,
    f.cldf_segments AS Form
FROM 
    LanguageTable AS l,
    FormTable AS f,
    ParameterTable AS p
WHERE
    f.cldf_parameterReference = p.cldf_id
        AND
    f.cldf_languageReference = l.cldf_id
        AND
    l.Selexion == 1
        AND
    -- Select the two concepts to compare
    p.concepticon_gloss IN (?, ?)
GROUP BY 
    l.cldf_name, f.cldf_segments
HAVING 
    COUNT > 1
ORDER BY 
    Family, Doculect;
