CREATE TEMP TABLE forms_with_cc AS
SELECT l.cldf_id         as Language_ID,
       l.cldf_name       as Language_Name,
       l.cldf_glottocode as Glottocode,
       l.Family,
       l.cldf_latitude as Latitude,
       l.cldf_longitude as Longitude,
       p.Concepticon_Gloss,
       cc(f.Dolgo_Sound_Classes) as Consonant_Classes
FROM LanguageTable as l,
     ParameterTable as p,
     FormTable as f
WHERE l.cldf_id = f.cldf_languageReference
  AND p.cldf_id = f.cldf_parameterReference
  AND p.Core_Concept like '%Swadesh-1955-100%'
  AND l.Selexion = 1
;