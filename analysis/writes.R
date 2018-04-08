linux.writes <- c(0.044771, 0.044475, 0.042985)
docker.writes <- c(0.096021, 0.092483, 0.093303)

mean(docker.writes)
# [1] 0.09393567
mean(linux.writes)
# [1] 0.044077
mean(linux.writes) * 1000
# [1] 44.077
mean(docker.writes) * 1000
# [1] 93.93567
mean(docker.writes) * 1000 - mean(linux.writes) * 1000
# [1] 49.85867
