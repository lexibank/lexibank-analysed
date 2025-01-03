SELECT 
    COUNT(DISTINCT(p.concepticon_gloss)) AS Count,
    l.cldf_name AS Doculect,
    l.cldf_glottocode AS Glottocode,
    l.family AS Family,
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
    -- Select the two concepts to compare
    p.concepticon_gloss IN ('SWEET POTATO', 'CASSAVA')
GROUP BY 
    l.cldf_name, f.cldf_segments
HAVING 
    COUNT > 1
ORDER BY 
    Family, Doculect;
