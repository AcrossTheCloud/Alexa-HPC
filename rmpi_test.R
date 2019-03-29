# Load the R MPI package if it is not already loaded.
if (!is.loaded("mpi_initialize")) {
    library("Rmpi")
    }

# get data from s3
library("aws.s3")
data <- read.csv(text = rawToChar(get_object(object = "s3://acrossthecloud-alexa-hpc/input.csv")), header=FALSE)
print(data[1,1])
print(data[1,2])
ns <- 2
mpi.spawn.Rslaves(nslaves=ns)
#
# In case R exits unexpectedly, have it automatically clean up
# resources taken up by Rmpi (slaves, memory, etc...)
.Last <- function(){
       if (is.loaded("mpi_initialize")){
           if (mpi.comm.size(1) > 0){
               print("Please use mpi.close.Rslaves() to close slaves.")
               mpi.close.Rslaves()
           }
           print("Please use mpi.quit() to quit R")
           .Call("mpi_finalize")
       }
}
# Tell all slaves to return a message identifying themselves
mpi.bcast.cmd( id <- mpi.comm.rank() )
mpi.bcast.cmd( ns <- mpi.comm.size() )
mpi.bcast.cmd( host <- mpi.get.processor.name() )
mpi.bcast.cmd( library("aws.s3") )
mpi.bcast.cmd( data <- read.csv(text = rawToChar(get_object(object = "s3://acrossthecloud-alexa-hpc/input.csv")), header=FALSE) )
mpi.remote.exec(paste("Worker",mpi.comm.rank(),"of",mpi.comm.size()-1,"computed the result of",data[1,1],"plus",data[1,2],"as",data[1,1]+data[1,2]))

# Tell all slaves to close down, and exit the program
mpi.close.Rslaves(dellog = FALSE)
mpi.quit()
