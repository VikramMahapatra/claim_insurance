provider "azurerm" {
  subscription_id = "adf26b12-8733-4b1d-8d7f-441d0bd42b73"
  features {}
  resource_provider_registrations     = "none"
}

# Fetch Azure Subscription ID dynamically
# data "azurerm_subscription" "current" {}

# Create a Resource Group (Only once)
resource "azurerm_resource_group" "rg" {
  name     = "rg-terraform-demo"
  location = "East US"
}
