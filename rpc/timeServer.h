/*
 * Please do not edit this file.
 * It was generated using rpcgen.
 */

#ifndef _TIMESERVER_H_RPCGEN
#define _TIMESERVER_H_RPCGEN

#include <rpc/rpc.h>


#ifdef __cplusplus
extern "C" {
#endif


#define TIME_PROG 0x20000001
#define TIMESERVER_VERS 1

#if defined(__STDC__) || defined(__cplusplus)
#define GET_TIME 1
extern  long * get_time_1(void *, CLIENT *);
extern  long * get_time_1_svc(void *, struct svc_req *);
extern int time_prog_1_freeresult (SVCXPRT *, xdrproc_t, caddr_t);

#else /* K&R C */
#define GET_TIME 1
extern  long * get_time_1();
extern  long * get_time_1_svc();
extern int time_prog_1_freeresult ();
#endif /* K&R C */

#ifdef __cplusplus
}
#endif

#endif /* !_TIMESERVER_H_RPCGEN */
