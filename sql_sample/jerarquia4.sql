select 
 case 
	when partido in (3316,4688) then 'derecha'
    when partido in (1079,4475) then 'centro'
	when partido in (3484) then 'izquierda'
    when partido in (3736,5033,4850,5008,5041,2744,5026) then 'extrema'
	when partido in (5008,4991,1528) then 'separatistas'
	when partido in (1533,4744,4223) then 'nacionalistas'
    else
         'inclasificable'
    end as categoria,
	sum(votes_presential)
from votos_provincia
group by categoria