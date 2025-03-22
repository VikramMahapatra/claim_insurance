# Reference the existing resource group
data "azurerm_resource_group" "rg" {
  name = azurerm_resource_group.rg.name
}

# Create a Virtual Network (VNet)
resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-demo"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  address_space       = ["10.0.0.0/16"]
}

# Create a Subnet inside the VNet
resource "azurerm_subnet" "subnet" {
  name                 = "subnet-demo"
  resource_group_name  = data.azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}
