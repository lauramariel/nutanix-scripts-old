#!/bin/bash
### Usage: cleanup_oss.sh <objectstorename>
### Run from Prism Central

#Fetch the object store name to delete/
ossname=$1

if [ $# -eq 0 ]
  then
    echo "Please pass in object store name to be deleted"
    exit 1
fi

read -p "Are you sure you want to delete $ossname? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
  echo "Confirmation not given, exiting"    
  exit 0
fi

echo "Deleting $ossname..."

#Create the query to fetch the object store from IDF.
cat > input.txt <<EOF
query {
   entity_list {
    entity_type_name: "objectstore"
   }
   where_clause {
    comparison_expr {
     lhs {
      leaf {
       column: "name"
      }
     }
     operator: kEQ
     rhs {
      leaf {
       value {
        str_value: "$ossname"
       }
      }
     }
    }
   }
   query_name: "where_clause"
  }
EOF

#Fetch the object store from IDF
python $HOME/bin/insights_rpc_tool.py --insights_rpc_method="GetEntitiesWithMetrics" --f="input.txt" >> /dev/null

#Get the entity ID from the above output
entity_id_in_idf=`cat output.txt | grep "entity_id" | cut -d':' -f2`

#Using the entity ID, form the next query to get the entity information.
cat > input.txt <<EOF
entity_guid_list {
 entity_type_name: "objectstore"
 entity_id : $entity_id_in_idf
}
EOF
python $HOME/bin/insights_rpc_tool.py --insights_rpc_method="GetEntities" --f="input.txt" >> /dev/null

#Get the CAS value for the above entity.
cas_value=`cat output.txt | grep "cas" | cut -d: -f2`
if [ -z $entity_id_in_idf ]; then
 echo "Unable to fetch object store uuid. Delete failed. Please manually delete object store entry from insights"
else
 #echo "Successfully fetched object store uuid: $entity_id_in_idf"
 let cas_value=cas_value+1
 cat > input.txt <<EOF
entity_guid {
 entity_type_name: "objectstore"
 entity_id: $entity_id_in_idf
}
cas_value: $cas_value
EOF
 #Delete the entity
 python $HOME/bin/insights_rpc_tool.py --insights_rpc_method="DeleteEntity" --f="input.txt" -o "output.txt" >> /dev/null
 echo "Successfully deleted $ossname"
 rm input.txt
 rm output.txt
fi
