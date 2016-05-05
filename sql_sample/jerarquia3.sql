select t3.padre as region,
      --t2.padre as provincia,
	   substr(municipio,1,2) as provincia,
	   municipio ,
	   partido,
	   --sum(votes_presential) --
	   votes_presential,votes_percent,seats,ord 
from votos_locales t1
--join geo_rel t2 on t2.hijo = municipio and t2.tipo_padre = 'P'
  join geo_rel t3 on substr(municipio,1,2) = t3.hijo and t3.tipo_padre = 'R'
--group by t3.padre,
--         t2.padre,
		 --municipio
--         partido 
