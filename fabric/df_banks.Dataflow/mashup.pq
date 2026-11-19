[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "banks_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared banks = let
  Source = Lakehouse.Contents([HierarchicalNavigation = null, EnableVorder = true, OutputMetadataRefresh = true]),
  #"Navigation 1" = Source{[workspaceId = "c5ec6974-346f-4e14-b98a-feb43d84fb9a"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "c50657c6-dd3a-4403-aa05-79c509e542f6"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Id = "banks", ItemKind = "Table"]}[Data],
  #"Inserted conditional column" = Table.AddColumn(#"Navigation 3", "bank_type", each if [is_internal] = true then "Internal" else "Participant")
in
  #"Inserted conditional column";
shared banks_DataDestination = let
  Pattern = Lakehouse.Contents([HierarchicalNavigation = true, EnableVorder = true, OutputMetadataRefresh = true, CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "c5ec6974-346f-4e14-b98a-feb43d84fb9a"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "c50657c6-dd3a-4403-aa05-79c509e542f6"]}[Data],
  Navigation_3 = Navigation_2{[Id = "dbo", ItemKind = "Schema"]}[Data],
  TableNavigation = Navigation_3{[Id = "dim_bank", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
