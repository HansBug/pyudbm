/*
  8 * 375000 = 3M of data points
*/
simulate 1200 [<=2*day] { tday[1].Ton, tday[1].Tget, discomfort, Global.energy } : 1 : false
