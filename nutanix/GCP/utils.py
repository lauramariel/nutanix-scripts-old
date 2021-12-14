"""
Manually ran utility to clear any orphaned clusters from the firestore
Orphaned clusters are clusters that are in the clusters collection, but not
in any pools collection, usually because of a crash
"""

from google.cloud import firestore
from datetime import datetime, timezone, timedelta

DB = firestore.Client(project="nutanix-testdrive-10")

xps = [
    "td2",
    "tdleap",
    "nx101",
    "calm",
    "prism",
    "xileap",
    "tddata",
    "era",
    "minehycu",
    "karbon",
    "clusters",
]


def get_cluster_names(cluster_type):
    """
    Calculates a full set of metrics
    Directly from Cloud Firestore
    """

    # Read all the clusters
    cluster_list = DB.collection(cluster_type).stream()
    stats = {}
    # Iterate through the list of clusters
    for cluster in cluster_list:
        # Convert the cluster snapshot obj to a dictionary
        cluster = cluster.to_dict()
        xp = cluster["tdtype"]
        status = cluster["status"]
        if not status:
            status = "unknown"
        if not stats.get(xp):
            stats[xp] = {
                "waiting": [],
                "active": [],
                "ready": [],
                "provisioning": [],
                "failed": [],
                "unknown": [],
            }
        # Update the stats dir
        if cluster["proxy_ready"] and status == "provisioning":
            stats[xp]["ready"].append(cluster["name"])
        else:
            stats[xp][status].append(cluster["name"])
    return stats


def search_clusters(ds, search="state", value="RELEASED"):
    """
    Calculates a full set of metrics
    Directly from Cloud Firestore
    """

    # Read all the clusters
    cluster_list = DB.collection(ds + "cluster").where(search, "==", value).stream()
    # Iterate through the list of clusters
    names = []
    for cluster in cluster_list:
        names.append(cluster.to_dict()["name"])
    return names


def get_gcp_ids(deploy_stage, tdtype="clusters", state="FAILED"):
    cluster_list = search_clusters(deploy_stage, "state", state)
    # Iterate through the list of clusters
    for cluster in cluster_list:
        cluster_info = get_cluster(cluster, deploy_stage)
        if cluster_info.get("tdtype") == tdtype:
            gcp_id = cluster_info.get("gcp_id")
            print(f"{gcp_id}")


def get_pool_clusters(pool_type):
    pool_clus = {}
    for xp in xps:
        pool_ref = DB.collection(pool_type).document(xp)
        pool = pool_ref.get().to_dict()
        pool_clus[xp] = {
            "waiting": pool["waiting"],
            "active": pool["active"],
            "ready": pool["ready"],
            "provisioning": pool["provisioning"],
            "failed": pool["failed"],
            "unknown": [],
        }
    return pool_clus


def orphaned_clusters(deploy_stage="stage", by_state=False, wrong_pool=False):
    pool_clus = get_pool_clusters(deploy_stage + "pool")
    clusters = get_cluster_names(deploy_stage + "cluster")
    orphaned_count = {}
    wrong = []
    for xp in xps:
        orphaned_count[xp] = {}
        orphaned_count[xp]["count"] = 0
        if by_state or wrong_pool:
            orphaned_count[xp]["clusters"] = {
                "waiting": [],
                "active": [],
                "ready": [],
                "provisioning": [],
                "failed": [],
                "unknown": [],
            }
        else:
            orphaned_count[xp]["clusters"] = []
    for xp in clusters:
        if pool_clus.get(xp):
            for state in clusters[xp]:
                for cluster in clusters[xp][state]:
                    if cluster not in pool_clus[xp][state]:
                        if wrong_pool:
                            for pool_state in pool_clus[xp]:
                                if cluster in pool_clus[xp][pool_state]:
                                    wrong.append(
                                        {
                                            "name": cluster,
                                            "wrong": state,
                                            "right": pool_state,
                                        }
                                    )
                        elif by_state:
                            orphaned_count[xp]["count"] = (
                                orphaned_count[xp]["count"] + 1
                            )
                            orphaned_count[xp]["clusters"][state].append(cluster)
                        else:
                            orphaned_count[xp]["count"] = (
                                orphaned_count[xp]["count"] + 1
                            )
                            orphaned_count[xp]["clusters"].append(cluster)
    if wrong_pool:
        return wrong
    else:
        return orphaned_count


def delete_orphans(deploy_stage="stage"):
    orphaned = orphaned_clusters(deploy_stage)
    for xp in orphaned:
        for cluster in orphaned[xp]["clusters"]:
            cluster_ref = DB.collection(deploy_stage + "cluster").document(cluster)
            cluster_ref.delete()


def associate_orphans(deploy_stage="stage"):
    orphaned = orphaned_clusters(deploy_stage, True)
    for xp in orphaned:
        for state in orphaned[xp]["clusters"]:
            this_set = orphaned[xp]["clusters"][state]
            if len(this_set) > 0:
                pool_ref = DB.collection(deploy_stage + "pool").document(xp)
                pool_ref.update({state: firestore.ArrayUnion(this_set)})


def get_all_clusters(deploy_stage="stage"):
    clusters = get_cluster_names(deploy_stage + "cluster")
    return clusters


def get_cluster(cluster_name, deploy_stage="stage"):
    clus_ref = DB.collection(deploy_stage + "cluster").document(cluster_name).get()
    if clus_ref.exists:
        cluster = clus_ref.to_dict()
        return cluster
    else:
        return False


def update_clusters(deploy_stage="stage"):
    orphaned = orphaned_clusters(deploy_stage, True)
    for xp in orphaned:
        for cluster_name in orphaned[xp]["clusters"]["waiting"]:
            cluster = get_cluster(cluster_name, deploy_stage)
            cluster[""]


def get_user_active_xp(email, deploy_stage="stage", xp=None):
    user_ref = DB.collection(deploy_stage + "user").document(email).get()
    user = user_ref.to_dict()
    if xp and user["active_xps"].get(xp):
        return user["active_xps"].get(xp)
    elif user:
        return user["active_xps"]
    else:
        return user


def delete_released_clusters(deploy_stage):
    clusters = search_clusters(deploy_stage, "state", "RELEASED")
    for cluster in clusters:
        print(f"Deleting {cluster}")
        doc = DB.collection(deploy_stage + "cluster").document(cluster)
        doc.delete()


def reverse_orphans(deploy_stage):
    pool_clus = get_pool_clusters(deploy_stage + "pool")
    clusters = get_cluster_names(deploy_stage + "cluster")
    orphaned_count = {}
    for xp in pool_clus:
        orphaned_count[xp] = {
            "waiting": [],
            "active": [],
            "ready": [],
            "provisioning": [],
            "failed": [],
            "unknown": [],
        }
        for status in pool_clus[xp]:
            for cluster in pool_clus[xp][status]:
                if cluster not in clusters[xp][status]:
                    print(f"{cluster} doesn't exist in DS")
                    orphaned_count[xp][status].append(cluster)
    return orphaned_count


def delete_list_orphans(deploy_stage):
    orphaned = reverse_orphans(deploy_stage)
    for xp in orphaned:
        for status in orphaned[xp]:
            if len(orphaned[xp][status]) > 0:
                pool_ref = DB.collection(deploy_stage + "pool").document(xp)
                pool_ref.update({status: firestore.ArrayRemove(orphaned[xp][status])})


def get_orphaned_state(deploy_stage):
    orphaned = orphaned_clusters(deploy_stage, True)
    rtn_list = []
    for xp in orphaned:
        for state in orphaned[xp]["clusters"]:
            for cluster in orphaned[xp]["clusters"][state]:
                rtn_list.append(get_cluster(cluster, deploy_stage))

    return rtn_list


def expiring_clusters(deploy_stage):
    clusters = get_all_clusters(deploy_stage)
    now = datetime.now(timezone.utc)
    expirecutoff = now + timedelta(hours=4)
    expired = []
    expiring = []
    for xp in clusters:
        for stat in clusters[xp]:
            for cluster in clusters[xp][stat]:
                cluster_data = get_cluster(cluster, deploy_stage)
                if not cluster_data:
                    print(f"{cluster} Does Not Exist")
                    continue
                gcp_expire = cluster_data["_Cluster__gcp_expire"]
                if gcp_expire and gcp_expire < expirecutoff:
                    print(f"{cluster}: {gcp_expire} - {cluster_data['gcp_id']}")
                    if gcp_expire < now:
                        expired.append(cluster_data.get("assigned_to"))
                    else:
                        expiring.append(cluster_data["gcp_id"])

    return expired, expiring


def tldr_clusters(deploy_stage):
    clusters = get_all_clusters(deploy_stage)
    now = datetime.now(timezone.utc)
    expirecutoff = now + timedelta(hours=6)
    for xp in clusters:
        for stat in clusters[xp]:
            for cluster in clusters[xp][stat]:
                cluster_data = get_cluster(cluster, deploy_stage)
                if not cluster_data:
                    print(f"{cluster} Does Not Exist")
                    continue
                gcp_expire = cluster_data["_Cluster__td_end"]
                if gcp_expire and gcp_expire > expirecutoff:
                    print(f"{cluster}: {gcp_expire} - {cluster_data['assigned_to']}")


# list clusters that are in provisioning status
def list_all_provisioning(deploy_stage):
    clusters = search_clusters(deploy_stage, "status", "provisioning")
    for cluster in clusters:
        cluster_info = get_cluster(cluster, deploy_stage)
        gcp_id = cluster_info.get("gcp_id")
        print(f"cluster: {cluster} gcp_id: {gcp_id}")


# list clusters that are in provisioning status but have no state assigned
def list_provisioning_no_state(deploy_stage):
    clusters = search_clusters(deploy_stage, "status", "provisioning")
    no_state_clusters = []
    for cluster in clusters:
        cluster_info = get_cluster(cluster, deploy_stage)
        gcp_id = cluster_info.get("gcp_id")
        state = cluster_info.get("state")
        print(f"{cluster} state: {state} gcp_id: {gcp_id}")
        if not state and gcp_id:
            no_state_clusters.append(cluster)

    return no_state_clusters


# check if there are any provisioning clusters with no state assigned
# that aren't in the pool and add them
def add_provisioning_to_pool(deploy_stage):
    clusters = search_clusters(deploy_stage, "status", "provisioning")
    for cluster in clusters:
        cluster_info = get_cluster(cluster, deploy_stage)
        gcp_id = cluster_info.get("gcp_id")
        state = cluster_info.get("state")
        tdtype = cluster_info.get("tdtype")
        if not state and gcp_id:
            print(f"Checking if {cluster} is in {deploy_stage}pool")
            # check if it's in the pool
            doc = DB.collection(deploy_stage + "pool").document(tdtype)
            ref = doc.get().to_dict()
            found = False
            for i in range(len(ref["provisioning"])):
                if ref["provisioning"][i] == cluster:
                    print(f"{cluster} found in prov list at index {i}")
                    found = True
            if not found:
                print(f"{cluster} was not found in provisioning list, adding it")
                ref["provisioning"].append(cluster)
                doc.set(ref, merge=True)


# delete clusters that are in provisioning state but have no gcp_id
def delete_invalid_provisioning(deploy_stage):
    clusters = search_clusters(deploy_stage, "status", "provisioning")
    for cluster in clusters:
        cluster_info = get_cluster(cluster, deploy_stage)
        gcp_id = cluster_info.get("gcp_id")
        if not gcp_id:
            print(f"Deleting cluster: {cluster} gcp_id: {gcp_id}")
            doc = DB.collection(deploy_stage + "cluster").document(cluster)
            doc.delete()
        else:
            print(f"Not deleting {cluster} because it has a valid gcp_id: {gcp_id}")


# list clusters that are in waiting status
def list_all_waiting(deploy_stage):
    clusters = search_clusters(deploy_stage, "status", "waiting")
    for cluster in clusters:
        cluster_info = get_cluster(cluster, deploy_stage)
        gcp_id = cluster_info.get("gcp_id")
        assigned_to = cluster_info.get("assigned_to")
        print(f"cluster: {cluster} assigned_to: {assigned_to} gcp_id: {gcp_id}")


# delete clusters that are in waiting state but have no gcp_id
# we have to delete from the user that it's assigned to also
def delete_invalid_waiting(deploy_stage):
    clusters = search_clusters(deploy_stage, "status", "waiting")

    for cluster in clusters:
        cluster_info = get_cluster(cluster, deploy_stage)
        gcp_id = cluster_info.get("gcp_id")
        assigned_to = cluster_info.get("assigned_to")
        if not gcp_id:
            print(f"Deleting cluster: {cluster} gcp_id: {gcp_id}")
            doc = DB.collection(deploy_stage + "cluster").document(cluster)
            doc.delete()
            print(f"Deleting cluster from active_xp list of {assigned_to}")
            if assigned_to:
                doc = DB.collection(deploy_stage + "user").document(assigned_to)
                try:
                    ref = doc.get().to_dict()
                    print("Active XPs " + str(ref["active_xps"]))
                    for xp in ref["active_xps"]:
                        if ref["active_xps"][xp]["name"] == cluster:
                            # delete the xp object from the user document
                            print(f"Deleting " + str(ref["active_xps"][xp]))
                            ref["active_xps"].pop(xp)
                            doc.set(ref)
                except Exception as e:
                    print(f"Caught exception: {e}")
                    continue
            else:
                print(f"No user assigned")
        else:
            print(f"Not deleting {cluster} because it has a valid gcp_id: {gcp_id}")
