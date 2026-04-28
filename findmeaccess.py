import argparse
import sys
import requests
import urllib3
import concurrent.futures
from termcolor import colored
import json
from tabulate import tabulate
import getpass
from datetime import datetime, timedelta
from lxml import etree
import base64
import uuid


# endpoint resources 
resources = {
    "Azure Graph API": "https://graph.chinacloudapi.cn",
    "Azure Management API": "https://management.chinacloudapi.cn",
#    "Azure Data Catalog": "https://datacatalog.azure.com",
    "Azure Key Vault": "https://vault.azure.cn",
#    "Cloud Webapp Proxy": "https://proxy.cloudwebappproxy.net/registerapp",
#    "Database": "https://database.windows.net",
    "Microsoft Graph API": "https://microsoftgraph.chinacloudapi.cn",
    "msmamservice": "https://msmamservice.api.application",
    "Office Management": "https://manage.office.com",
    "Office Apps": "https://officeapps.live.com",
#    "OneNote": "https://onenote.com",
#    "Outlook": "https://outlook.office365.com",
#    "Outlook SDF": "https://outlook-sdf.office.com",
#    "Sara": "https://api.diagnostics.office.com",
#    "Skype For Business": "https://api.skypeforbusiness.com",
    "Spaces Api": "https://api.spaces.skype.com",
#    "Webshell Suite": "https://webshell.suite.office.com",
    "Windows Management API": "https://management.core.chinacloudapi.cn",
#    "Yammer": "https://api.yammer.com"
}

# used for final display
final_results = {}

# https://github.com/secureworks/family-of-client-ids-research/blob/main/known-foci-clients.csv
# some from here too after filtering: https://learn.microsoft.com/en-us/troubleshoot/azure/active-directory/verify-first-party-apps-sign-in
client_ids = {
	"Dataverse" : "00000007-0000-0000-c000-000000000000",
	"PowerPlatformAdminCenter" : "065d9450-1e87-434e-ac2f-69af271549ed",
	"Power Apps" : "4e291c71-d680-4d0e-9640-0a3358e31177",
	"Finance Copilot" : "8c1a9936-578e-4d13-9bd9-9afe53ef7de8",
	"Dynamics365Assistant" : "d024ca46-2708-4d20-903e-b18b7e1d95dc",
	"MicrosoftServiceCopilot-Prod" : "61ccfc51-60d1-470a-9dca-f78fcf640d23",
	"EHRTeleHealth" : "e97edbaf-39b2-4546-ba61-0a24e1bef890",
	"d365-dani-exceladdinprod" : "7c4f9118-450a-4e75-b96b-df2d0cac4c0d",
	"Power BI Desktop" : "7f67af8a-fedc-4b08-8b4e-37c4d127b6cf",
	"MicrosoftPowerBI" : "871c010f-5e61-4fb1-83ac-98610a7e9110",
	"Mix Tools API" : "8463278f-7a65-4b3d-903c-5e66a2ad1164",
	"PowerPlatform-commondataserviceforapps-Connector" : "5e72ef24-048b-4aae-8fd6-8653ce2d6760",
	"sophia.api.microsoft.com" : "d0af0b2c-272b-4820-80ce-af3cc751950f",
	"Sophia Platform Service API" : "d8fa9ca8-15de-4a33-b719-9c944b9b2e3e",
	"QueryFormulationService" : "66a88757-258c-4c72-893c-3e8bed4d6899",
	"Prod M365FLWPService Prod" : "325e8307-defd-47df-aeff-15152ea6e5bf",
	"Prod M365FLWPClient Prod" : "226e4631-c980-4b11-9c96-5e26bb14dafc",
	"Prod M365FLWPService FirstRelease" : "9e6d7425-da52-4c9d-a3bf-48ce4670f9ef",
	"Prod M365FLWPClient FirstRelease" : "e582717c-581c-4a51-a8d7-5cd28f59497a",
	"Microsoft Dynamics CRM for Microsoft Office Outlook" : "2f29638c-34d4-4cf2-a16a-7caf612cee15",
	"WPSTrialSignUpService_Prod" : "ebf6b2b7-c635-4217-b6b7-21de4ac65764",
	"Biz Apps Demo Hub Prod" : "46e9667d-34e6-43d8-a494-6759b3ae6a5e",
	"Visual Studio" : "04f0c124-f2bc-4f59-8241-bf6df9866bbd",
	"Power Platform Admin Center Client Test" : "c84a0f23-a0f8-4e8e-918b-57db620d110a",
	"make.test.powerapps.com" : "719640cd-0337-4b0c-8e6a-431271371fab",
	"Teams Approvals" : "3e050dd7-7815-46a0-8263-b73168a42c10",
	"SharePointOnlineWebClientExtensibility" : "08e18876-6177-487e-b8b5-cf950c1e598c",
	"Viva Goals Integrations" : "bee5ee7b-22c7-4e94-9b8b-031319e230a3",
	"Customer Experience Platform FRE PROD" : "6f459c5d-d670-409b-83a6-68b040f4cb78",
	"Customer Experience Platform FRE TIP Non-Prod" : "f10573e9-a3c7-41b4-b203-4b1baed8fc8c",
	"make.test.powerapps.com" : "60f38cf4-a0bf-4fdf-b0b5-14d3131bc031",
	"Cloud for Nonprofit Installer" : "a0fe4328-8965-437b-a350-cf71409d002f",
	"Minit Desktop for Windows" : "5c17a0cf-5493-4b86-b23d-dabc1cc46f5a",
	"PhysOps.Clients.Worker" : "04d97d71-f71f-450b-8b44-f638d5d1b5d6",
	"Microsoft.Data.SqlClient" : "2fd908ad-0664-4344-b9be-cd3e8b574c38",
	"make.gov.powerpages.microsoft.us" : "929cb005-cba1-40c4-a962-ef441029cb6c",
	"Azure API Management Portal extension" : "73a510c3-9946-46dd-b5ae-a8f0ae68fd04",
	"SuplariDev" : "38ec0b21-8bde-4473-950b-819ceb3ed233",
	"Teams Work Report" : "ea62c1c6-550b-4238-8ea7-c55a85d86be8",
	"LobeClientDev" : "bd414a4d-005a-4a51-a63e-12097e3dcd19",
	"Visual Studio Code" : "aebc6443-996d-45c2-90f0-388ff96faa56",
	"D365SalesProductivityProvisioning" : "4787c7ff-7cea-43db-8d0d-919f15c6354b",
	"make.test.powerpages.microsoft.com" : "f9a5ac11-cab3-45f0-9d0f-83463ba2e34c",
	"make.powerpages.microsoft.com" : "75eb2b80-011a-4693-9a47-7971c853603c",
	"Dynamics 365 collaboration with Microsoft Teams" : "a8adde6c-aeb4-4fd6-9d8f-c2dfdecac60a",
	"Project Madeira" : "996def3d-b36c-4153-8607-a6fd3c01b89f",
	"Power Platform CLI - pac" : "9cee029c-6210-4654-90bb-17e6e9d36617",
	"M365AdminServices" : "6b91db1b-f05b-405a-a0b2-e3f60b28d645",
	"Power Cards" : "2f7b4d11-d621-4079-9798-27f548d681f1",
	"Dynamics 365 Customer Insights - Consent - DEV" : "8b66798c-a359-423d-8d71-567ee6da1016",
	"Supply Chain Windblade Development" : "50d9b7e0-07b6-4615-a8ae-f7f017db392a",
	"Microsoft Dynamics 365 Supply Chain Visibility" : "d6037e40-282c-493d-8f63-f255e36c6ef4",
	"Lobe" : "37ff607d-6be1-4c1b-a5f8-e5ad92b55975",
	"TrustedPublishersProxyService-DoD" : "22618bd1-b6aa-45f0-8ebd-718d158d888d",
	"TrustedPublishersProxyService-GccModerate" : "e8c38929-689f-4155-96f7-ab45b0f67cec",
	"TrustedPublishersProxyService" : "2b61b865-d0bd-4c60-9efa-6fa934eefaac",
	"Unify Portal Prod" : "9f4bb91b-347a-47ab-aba4-06db0dcb89e3",
	"BAGSolutionsInstaller" : "de490f5e-b798-48d8-ae3b-c220d7494cef",
	"PowerVirtualAgentsUSGovGCC" : "9315aedd-209b-43b3-b149-2abff6a95d59",
	"SharePointMigrationTool" : "fdd7719f-d61e-4592-b501-793734eb8a0e",
	"BingTest" : "ef47e344-4bff-4e28-87da-6551a21ffbe0",
	"Bing" : "9ea1ad79-fdb6-4f9a-8bc3-2b70f96e34c7",
	"Power Apps Portals - Development" : "09be0be4-1874-4f49-bc5c-78e6fc2a8065",
	"Power Automate Desktop For Windows" : "386ce8c0-7421-48c9-a1df-2a532400339f",
	"Dynamics 365 Customer Insights - Consent" : "9e3b502c-b4a1-441d-98fd-28e482bf7e88",
	"Search Federation Connector - Dataverse" : "9c60a40b-b5c5-4d01-8588-776209c80db3",
	"CRM Power BI Integration GCC High" : "03509b1f-54e9-4557-a555-19a090903b84",
	"Media Recording for Dynamics 365 Sales" : "f448d7e5-e313-4f90-a3eb-5dbb3277e4b3",
	"Media Recording for Dynamics 365 Sales - TIP" : "883d98cb-7d92-43b7-a194-07e51a2fa5bb",
	"Business Central to Common Data Service" : "88c57617-94ff-4043-a396-8a85a8d38922",
	"eSeal" : "19679030-48d8-445f-b27c-311bb3be8a2c",
	"PADWAMigratorGCC" : "19a92965-3c11-4ed7-a1bd-9b66785dd4c6",
	"PADWAMigratorGCCHigh" : "cb47b44e-c0a3-47a5-85ce-3dc039c85e80",
	"PADWAMigrator" : "133c4dc0-9d5f-4826-9f7b-6bb3d3867e6a",
	"BAGSolutionsInstallerTest" : "8ad75a3e-ae97-457c-baab-65bd5c95389f",
	"Power Automate Desktop DoD" : "ae7deb89-ca76-4073-bf3e-b72165ac58e9",
	"Power Automate Desktop GCC High" : "f1a1e36a-d61f-4283-9f48-0867636e332c",
	"Power Automate Desktop GCC" : "041e4c2d-ba3e-46a1-9347-5bc4054c8af4",
	"ConnectedFieldServiceDeployment" : "3852314e-aab9-42c3-a859-5b5b88a90000",
	"RSOProvisioningCustomerDashboard" : "2f6713e6-1e21-4a83-91b4-5bf9a2378f81",
	"Dynamics CRM TIP SRS" : "257fc75b-c7b8-434b-a467-fcfc16cb7ab6",
	"ProcessSimpleDoD" : "a6d2002e-7db6-4da0-94e8-73765fdbc7fb",
	"Power Automate Desktop" : "ee90a17f-1cb7-4909-be27-dfc2dcc4dc15",
	"Dynamics 365 Human Resources LinkedIn Adapter App" : "3a225c96-d62a-44ce-b3ec-bd4e8e9befef",
	"Power BI Report Builder" : "f0b72488-7082-488a-a7e8-eada97bd842d",
	"Dynamics 365 Connected Store" : "291bcb22-15e5-4341-8f91-feb152d655ee",
	"ApiHub-Connectors-DoD" : "363a906a-1ceb-41ea-9f20-884c694f2fc2",
	"MicrosoftFlowDoD" : "7abdc2e3-67d5-4ccf-8138-e133192788e3",
	"MicrosoftFlowGCCHigh" : "470d0752-cb06-49b2-ac83-5023fc23adae",
	"MicrosoftFlowGCC" : "50351660-e7b1-4621-8bc8-8503296a5535",
	"Dynamics365AICustomerInsights" : "0bfc4568-a4ba-4c58-bd3e-5d3e76bd7fff",
	"MicrosoftUnifiedCustomerIntelligence" : "38c77d00-5fcb-4cce-9d93-af4738258e3c",
	"AzureADIdentityGovernanceUserManagement" : "ec245c98-4a90-40c2-955a-88b727d97151",
	"AzureADIdentityGovernanceEntitlementManagement" : "810dcf14-1858-4bf2-8134-4c369fa3235b",
	"MicrosoftFormsProTest" : "19dd5b37-d116-48cb-90d2-4aa56696cba1",
	"Power Query Online GCC-L5" : "8c8fbf21-0ef3-4f60-81cf-0df811ff5d16",
	"PowerApps Web Player Service - play.apps.appsplatform.us" : "adc59501-b8c1-453a-a88b-9f4b244c1631",
	"PowerApps Web Player Service - high.apps.powerapps.us" : "dc426ec9-396a-46fd-8445-564554907e34",
	"PowerApps Web Player Service - apps.gov.powerapp.us" : "282c9137-f94e-4287-8223-9b60f2974e5c",
	"apps.powerapps.com" : "9362bc14-3e81-4ef9-8b77-f1c40afe68e0",
	"PowerPlatformAdminCenter" : "065d9450-1e87-434e-ac2f-69af271549ed",
	"Power Query Online GCC-L4" : "ef947699-9b52-4b31-9a37-ef325c6ffc47",
	"Omnichannel for CS Admin App Prod" : "fcf50ee5-8107-45e4-9a37-838727a360f5",
	"Azure API Hub - GCC-Med" : "d93420f9-abc8-46b7-b7fc-30ec1f007ee2",
	"Power Query Online GCC-L2" : "939fe80f-2eef-464f-b0cf-705d254a2cf2",
	"OmnichannelCRMClient" : "d9ce8cfa-8bd8-4ff1-b39b-5e5dd5742935",
	"OmnichannelEngagementHubAdminApp" : "2c37df23-0c28-4fbf-9b2a-d5fd6277bf92",
	"DYN365_CS_MESSAGING" : "3957683c-3a48-4a6c-8706-a6e2d6883b02",
	"ApiHub-Connectors-GCCHigh" : "36ee54ac-414c-41ef-afde-2ddfd25d5408",
	"Azure Synapse Link for Dataverse" : "7f15f9d9-cad0-44f1-bbba-d36650e07765",
	"PrcessSimpleGCCHigh" : "9856e8dd-37b6-4749-a54b-8f6503ea93b7",
	"CRM Power BI Integration GCC" : "bb0fc165-b959-4e50-a8fc-309c1193e396",
	"PowerApps - play.apps.appsplatform.us" : "44a34657-125d-4be1-b08d-87a07b336d24",
	"PowerApps - apps.high.powerapps.us" : "b145fb8f-d278-464f-8de1-894b596ecbde",
	"PowerApps - apps.gov.powerapps.us" : "a81833f1-fd18-490b-8598-60cd7b6b0382",
	"mil.create.powerapps.us" : "d7e0a6a1-dde5-4f6e-81ce-781fa7483834",
	"high.create.powerapps.us" : "58acb57d-f51b-4993-8f4a-4e41ad77e481",
	"PowerApps Fairfax" : "a4b559be-784e-49ec-9b63-7208442255e1",
	"PowerApps" : "0cb2a3b9-c0b0-4f92-95e2-8955085f78c2",
	"PowerApps - apps.powerapps.com" : "3e62f81e-590b-425b-9531-cad6683656cf",
	"Aria" : "cd34d57a-a3ef-48b1-b84b-9686f0f7c099",
	"CrmSalesInsightsRA" : "6e7d203a-179d-4ae0-87da-a77dd8aa3135",
	"make.mil.powerapps.us" : "fac5b0fe-9b16-4ae3-b20b-324ec3f033d3",
	"make.high.powerapps.us" : "5d21c8e8-6d68-4b62-a3a5-bc1900513fad",
	"make.gov.powerapps.us" : "feb2c8aa-4f70-4881-abec-521141627b04",
	"Field Service Mobile" : "0ef09fa7-413d-4a9f-a7a5-32f8f62b7598",
	"MR.Mty.App" : "32166110-0424-4622-8b0d-4e50f4da7a74",
	"APIHub-Connectors-GCC_notUsed" : "9a375489-421a-4af5-9f4a-3dd5a8f7b0d8",
	"ProcessSimpleGCC" : "38a893b6-d74c-4786-8fe7-bc3b4318e881",
	"DYN365AISERVICEINSIHTSPPE" : "11f6c209-c042-4da5-acb9-8d3546fe506f",
	"CrmSalesInsightsTIP" : "b80a77b1-a78c-4655-9283-e40bbc285af0",
	"PowerAppsGov" : "c6d1e3ad-0185-40e0-a11b-0542b185d12c",
	"ccibotsprod" : "96ff4394-9197-43aa-b393-6a41652e21f8",
	"MSRemoteAssist" : "fca5a20d-55aa-4395-9c2f-c6147f3c9ffa",
	"Field Service Mobile" : "110797d6-4a5e-4e58-a06d-f1bf3f3a8069",
	"MicrosoftDynamics365MRGuidesCoreClient" : "655db33f-4580-4e63-bad1-4618764badb9",
	"ccibots" : "a59cef1e-2e32-4703-8dab-810d9807efeb",
	"CCIBot" : "a522f059-bb65-47c0-8934-7db6e5286414",
	"MicrosoftDynamics365OfficeAppsIntegration" : "44a02aaa-7145-4925-9dcd-79e6e1b94eff",
	"PowerApps" : "4e291c71-d680-4d0e-9640-0a3358e31177",
	"CrmSalesInsights" : "b20d0d3a-dc90-485b-ad11-6031e769e221",
	"Dynamics 365 for Marketing" : "5a24b264-c8f3-474d-92f6-a998cca942c1",
	"DYN365AISERVICEINSIGHTS" : "60d240cc-7621-469e-80f1-584c53e9cafa",
	"make.powerapps.com" : "a8f7a65c-f5ba-4859-b2d6-df772c264e9d",
	"Connectors" : "48af08dc-f6d2-435f-b2a7-069abd99c086",
	"CRM Groups Integration" : "b15cc146-2b25-46c7-90c1-daa6c3e8386b",
	"make.powerpages.microsoft.com" : "945d3a88-db20-40bd-a9e3-8f2383a17c88",
	"CrmExporter" : "b861dbcc-a7ef-4219-a005-0e4de4ea7dcf",
	"Lobe Client" : "0b820e0a-8d08-45d1-8740-bde894f7e1c2",
	"TrustedPublishersProxyServicePPE" : "3d3f56ed-9c38-4480-b172-0fa5d8838516",
	"Power BI" : "00000009-0000-0000-c000-000000000000",
	"BizQA for CDS" : "aeb01831-b358-4750-92ce-722e4f3ea7e8",
	"Dynamics 365 Field Service" : "8d25f88c-09fe-41eb-9ee1-0545adf985df",
	"Azure AD Identity Governance - Dynamics 365 Management" : "c495cfdc-814f-46a1-89f0-657921c9fbe0",
	"Power Platform API" : "8578e004-a5c6-46e7-913e-12f58912df43",
	"App Service" : "7ab7862c-4c57-491e-8a45-d52a7e023983",
	"Microsoft Dynamics CRM for tablets and phones" : "ce9f9f18-dd0c-473e-b9b2-47812435e20d",
	"CRM Power BI Integration" : "e64aa8bc-8eb4-40e2-898b-cf261a25954f",
	"Microsoft Customer Engagement Portal" : "71234da4-b92f-429d-b8ec-6e62652e50d7",
	"Microsoft Power Query for Excel" : "a672d62c-fc7b-4e81-a576-e60dc46e951d",
	"Microsoft Flow Portal" : "6204c1d1-4712-4c46-a7d9-3ed63d992682",
	"Portfolios" : "f53895d3-095d-408f-8e93-8f94b391404e",
	"Power BI Data Refresh" : "b52893c8-bc2e-47fc-918b-77022b299bbc",
	"Dynamics 365 Development Tools" : "2ad88395-b77d-4561-9441-d0e40824f9bc",
	"Microsoft Flow Service" : "7df0a125-d3be-4c96-aa54-591f83ff541c",
	"Microsoft Power Query" : "f3b07414-6bf4-46e6-b63f-56941f3f4128",
	"Microsoft Office" : "d3590ed6-52b3-4102-aeff-aad2292ab01c",
	"Dynamics 365 Example Client Application" : "51f81489-12ee-4a9e-aaae-a2591f45987d",
	"Microsoft Business Office Add-in" : "2bc50526-cdc3-4e36-a970-c284c34cbd6e",
	"Microsoft Dynamics CRM App for Outlook" : "60216f25-dbae-452b-83ae-6224158ce95e",
	"Microsoft Teams" : "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
	"Dynamics CRM Unified Service Desk" : "4906f920-9f94-4f14-98aa-8456dd5f78a8",
	"SQL DotNet Client" : "4d079b4c-cab7-4b7c-a115-8fd51b6f8239",
	"Microsoft Azure CLI" : "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
	"ODBC Client Driver" : "2c1229aa-16c5-4ff5-b46b-4f7fe2a2a9c8",
	"Dynamics Data Integration" : "2e49aa60-1bd3-43b6-8ab6-03ada3d9f08b",
	"Azure SQL Database and Data Warehouse" : "a94f9c62-97fe-4d19-b06d-472bed8d2bcf",
	"JDBC Client Driver" : "7f98cb04-cd1e-40df-9140-3bf7e2cea4db",
	"Dynamics Retail Modern POS" : "d6b5a0bd-bf3f-4a8c-b370-619fb3d0e1cc",
	"Microsoft Teams Web Client" : "5e3ce6c0-2b1f-4285-8d4b-75ee78787346",
	"Microsoft Azure PowerShell" : "1950a258-227b-4e31-a9cf-717495945fc2",
	"Microsoft Dynamics 365 Project Service Automation Add-in for Microsoft Project" : "2f3b013e-5dc4-4b2a-831f-47ba08353237",
	"SharePoint" : "d326c1ce-6cc6-4de2-bebc-4591e5e13ef0",
	"Outlook Mobile" : "27922004-5251-4030-b22d-91ecd9a37ea4",
	"Microsoft.Azure.Services.AppAuthentication" : "d7813711-9094-4ad3-a062-cac3ec74ebe8",
	"Visual Studio" : "872cd9fa-d31f-45e0-9eab-6e460a02d1f1",
	"Azure Data Factory" : "a306baf0-5ad8-4f6f-babf-6a286b0142ba",
	"Microsoft Authenticator App" : "4813382a-8fa7-425e-ab75-3b753aab3abb",
	"Microsoft Power BI Government Community Cloud" : "fc4979e5-0aa5-429f-b13a-5d1365be5566",
	"Power BI Data Refresh" : "34cc6120-8c17-428c-b5aa-bede141fb74a",
	"Power BI Gateway" : "ea0616ba-638b-4df5-95b9-636659ae5121",
	"Microsoft Mashup Engine" : "f40b99cd-675e-4ce8-ae86-47b77d2a9c4d",
	"SharePoint Android" : "f05ff7c9-f75a-4acd-a3b5-f4b6a870245d",
	"Dynamics RCS Workload" : "091c98b0-a1c9-4b02-b62c-7753395ccabe",
	"Microsoft Flow" : "57fcbcfa-7cee-4eb1-8b25-12d2030b4ee0",
	"Microsoft Power BI" : "c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12",
	"Microsoft To-Do client" : "22098786-6e16-43cc-a27d-191a01a1e3b5",
	"Microsoft Edge" : "f44b1140-bc5e-48c6-8dc0-5cf5a53c0e34",
	"Microsoft Dynamics CRM Learning Path" : "2db8cb1d-fb6c-450b-ab09-49b6ae35186b",
	"OneDrive" : "b26aadf8-566f-4478-926f-589f601d9c74",
	"Project Finder Mobile" : "dd63a01a-ae84-4d07-bf60-69dadeaa8c89",
	"Microsoft Teams Services" : "cc15fd57-2c6c-4117-a88c-83b1d56b4bbe",
	"Azure Portal" : "c44b4083-3bb0-49c1-b47d-974e53cbdf3c",
	"Azure Active Directory PowerShell" : "1b730954-1685-4b74-9bfd-dac224a7b894",
	"Microsoft Flow CDS Integration Service" : "0eda3b13-ddc9-4c25-b7dd-2f6ea073d6b7",
	"Microsoft Planner" : "66375f6b-983f-4c2c-9701-d680650f588f",
	"Microsoft Intune Company Portal" : "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223",
	"Office 365 Management" : "00b41c95-dab0-4487-9791-b9d2c32c80f2",
	"Windows Search" : "26a7ee05-5602-4d76-a7ba-eae8b7b67941",
	"Enterprise Roaming and Backup" : "60c8bde5-3167-4f92-8fdb-059f6176dc0f",
	"Aadrm Admin Powershell" : "90f610bf-206d-4950-b61d-37fa6fd1b224",
	"Microsoft Azure Active Directory Connect" : "cb1056e2-e479-49de-ae31-7812af012ed8",
	"Office365 Shell WCSS-Client" : "89bee1f7-5e6e-4d8a-9f3d-ecd601259da7",
	"Microsoft Dynamics ERP" : "00000015-0000-0000-c000-000000000000",
	"Microsoft Dynamics Document Routing Agent" : "cf8f0657-7610-4b05-8723-a4322ae045c6",
	"Dynamics CRM Online Administration" : "637fcc9f-4a9b-4aaa-8713-a2a3cfda1505",
	"Office 365 Exchange Online" : "00000002-0000-0ff1-ce00-000000000000",
	"Microsoft SharePoint Online Management Shell" : "9bc3ab49-b65d-410a-85ad-de819febfddc",
	"Azure Data Studio" : "a69788c6-1d43-44ed-9ca3-b83e194da255",
	"Azure Analysis Services Client" : "cf710c6e-dfcc-4fa8-a093-d47294e44c66",
	"Microsoft Whiteboard Client" : "57336123-6e14-4acc-8dcf-287b6088aa28",
	"OneDrive SyncEngine" : "ab9b8c07-8f02-4f72-87fa-80105867a763",
	"OneDrive Photos" : "bed12bc0-3a62-470d-998c-e47546e7b039",
	"OneDrive iOS App" : "af124e86-4e96-495a-b70a-90f90ab96707",
	"Microsoft Edge" : "e9c51622-460d-4d3d-952d-966a5b1da34c",
	"SharePoint Online Client Extensibility" : "c58637bb-e2e1-4312-8a00-04b5ffcd3403",
	"Microsoft Device Registration Client" : "dd762716-544d-4aeb-a526-687b73838a22",
	"Universal Store Native Client" : "268761a2-03f3-40df-8a8b-c3db24145b6b",
	"Windows Spotlight" : "1b3c667f-cde3-4090-b60b-3d2abd0117f0",
	"Microsoft Intune Windows Agent" : "fc0f3af4-6835-4174-b806-f7db311fd2f3",
	"Dynamics 365 Sales" : "59d7fccf-1f97-4a79-bb78-e722112f9862",
	"DeflectionTest" : "600def3d-4cdb-465f-9dad-dce96b255d6a",
	"CDSUserManagementNonProd" : "db966cd2-032b-4f21-b7c2-eadd3d68c2f2",
	"DeflectionPreProd" : "5443ef98-eb7c-4354-8367-f35dffe3cba7",
	"PowerAppsCustomerManagementPlaneBackend" : "585738fa-4b8c-4f90-b926-7eab8c498c69",
	"DataSyncService" : "ab9468a9-c559-47ec-86f6-2f1b48612c09",
	"PowerAutomate-ProcessMining" : "dad3c6de-ed58-42ef-989f-9c0303aaeedc",
	"AppDeploymentOrchestration" : "886d9650-b672-4531-b16f-4617b5492d2f",
	"RelevanceSearch" : "f034940d-60b7-4587-afc9-ac1786ad7419",
	"CCaaSCRMClient" : "edfdd43b-26b5-498b-b89f-515ddf78dcc2",
	"PowerAutomate-ProcessMining-PPE" : "c4c008ec-e9c5-455c-b7e3-92c49982bc84",
	"PowerAutomate-ProcessMining-DEV" : "630e0ac2-6aa6-41bd-b950-5ade41828d3a",
	"PowerAutomate-ProcessMining-TEST" : "e1255f48-529f-4573-8ad2-8b13d784cd1c",
	"PowerAppsDataPlaneBackend" : "dac3dc4c-8be0-4972-8c97-e0a8500927f3",
	"Flow-CDSNativeConnectorTIP2US" : "de8e0d25-0c9e-4230-87d6-cf379be2f1bd",
	"SIAutoCapture" : "b9f7f9ce-78c7-4651-8663-c2ba51a2556a",
	"DynamicsInstallerTest" : "079013fb-85d0-4d99-87d0-aeca060231e3",
	"JobsServicePreProd" : "fa69122a-0a5e-41f1-beed-ca317370fb56",
	"AIBuilder_StructuredML_PreProd_CDS" : "0527d918-8aec-4c44-9f4e-86cc8b88d87b",
	"Omnichannel" : "c9b24c1a-09c1-4726-a288-709c86a12a9b",
	"PowerPlatformEnvironmentManagement" : "a7d42dcf-5f3b-41b0-8ad5-e7c5808c617a",
	"Flow-RP" : "bdb3d4c5-dc11-426e-8f04-2621dbcce738",
	"TPSProxyServiceTST" : "de9fe347-3128-4a28-9b19-cd4ecca1f526",
	"InsightsAppsPlatform" : "7255edad-9269-44d0-b153-92ceffbf86fa",
	"CatalogServiceTest" : "7a7f0ba2-519f-49eb-9b86-1a967ba231f3",
	"Finance and Operations Runtime Integration User - TST Geo" : "71684101-1068-40b0-a0da-062710e1040d",
	"AppDeploymentOrchestration-Preprod" : "ce384d7c-6755-471d-91aa-1b48cc519c49",
	"BAP CDS Application" : "978b42f5-e03a-4695-b8df-454959d032c8",
	"Common Data Service User Management" : "c92229fa-e4e7-47fc-81a8-01386459c021",
	"Dynamics 365 Sales Service" : "44f229e1-5c76-4d68-8b7c-83cbfd54ab7a",
	"Relevance Search Service" : "1884bdbf-452a-4a11-9c76-afdbdb1b3768",
	"PowerApps CDS Service" : "27f13ec4-0f4e-4840-b547-1a0181666256",
	"Product Insights - CDS to Azure data lake - app" : "ffa7d2fe-fc04-4599-9f6d-7ca06dd0c4fd",
	"ApolloNonProdFirstParty" : "265378aa-7259-4b82-af51-0c97c6cbc0ca",
	"AI Builder Prod - CDS to Azure data lake" : "8b62382d-110e-4db8-83a6-c7e8ee84296a",
	"GlobalDiscoService2" : "97d27433-255e-498c-a280-0cbc9aee407e",
	"Common Data Service Managed Data Lake Service" : "546068c3-99b1-4890-8e93-c8aeadcfe56a",
	"Common Data Service Global Discovery Service" : "6eb29b24-9d89-4f26-bf2f-9a84ed2499b8",
	"Dynamics 365 CCA Prod - CDS to Azure data lake" : "299fa2bd-f53a-45b1-b501-1056398454bc",
	"MicrosoftSocialEngagement@microsoft.com" : "e8ab36af-d4be-4833-a38b-4d6cf1cfd525",
	"Flow Xrm System User" : "fbc61429-7762-4b4a-8f9d-c728a1a5e792",
	"MicrosoftCrmDataSync@microsoft.com" : "7a575ec8-8d12-42eb-9edc-b93f3aa92c48",
	"Dynamics 365 Customer Insights Prod - CDS to Azure data lake" : "6ec6a75c-d04e-4613-92da-069f88c74a13",
	"Dynamics 365 CCA Data analytics Prod - CDS to Azure data lake" : "87684a6d-f115-436c-a231-6a4d08eb01a6",
	"ApolloProdFirstParty" : "8c04f0eb-27fc-44cc-9e48-914b9202890a",
	"DynamicsCRMCortanaCacheService@microsoft.com" : "d4a55fa7-2c20-434d-8942-689200452979",
	"Microsoft Dynamics Jobs Service" : "e548fb5c-c385-41a6-a31d-6dbc2f0ca8a3",
	"SQLDBControlplanefirstpartyApp" : "ceecbdd6-288c-4be9-8445-74f139e5db19",
	"Accounts Control UI" : "a40d7d7d-59aa-447e-a655-679a4107e548",
	"Copilot App" : "14638111-3389-403d-b206-a6a71d9f8f16",
    	"Designer App" : "598ab7bb-a59c-4d31-ba84-ded22c220dbd",
    	"Editor Browser Extension" : "1a20851a-696e-4c7e-96f4-c282dfe48872",
    	"Enterprise Roaming and Backup" : "60c8bde5-3167-4f92-8fdb-059f6176dc0f",
    	"Get Help" : "1f7f6f43-2f81-429c-8499-293566d0ab0c",
    	"Intune MAM" : "6c7e8096-f593-4d72-807f-a5f86dcc9c77",
    	"Loop" : "0922ef46-e1b9-4f7e-9134-9ad00547eb41",
    	"M365 Compliance Drive Client" : "be1918be-3fe3-4be9-b32b-b542fc27f02e",
    	"Managed Home Screen" : "3b68e96c-82d3-41b3-99b8-56c260cf38d8",
    	"Microsoft 365 Copilot" : "0ec893e0-5785-4de6-99da-4ed124e5296c",
    	"Microsoft Authentication Broker" : "29d9ed98-a469-4536-ade2-f981bc1d605e",
    	"Microsoft Authenticator App" : "4813382a-8fa7-425e-ab75-3b753aab3abb",
    	"Microsoft Azure CLI" : "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
    	"Microsoft Azure PowerShell" : "1950a258-227b-4e31-a9cf-717495945fc2",
    	"Microsoft Bing Search for Microsoft Edge" : "2d7f3606-b07d-41d1-b9d2-0d0c9296a6e8",
    	"Microsoft Bing Search" : "cf36b471-5b44-428c-9ce7-313bf84528de",
    	"Microsoft Defender for Mobile" : "dd47d17a-3194-4d86-bfd5-c6ae6f5651e3",
    	"Microsoft Defender Platform" : "cab96880-db5b-4e15-90a7-f3f1d62ffe39",
    	"Microsoft Docs" : "18fbca16-2224-45f6-85b0-f7bf2b39b3f3",
    	"Microsoft Edge Enterprise New Tab Page" : "d7b530a4-7680-4c23-a8bf-c52c121d2e87",
    	"Microsoft Edge MSAv2" : "82864fa0-ed49-4711-8395-a0e6003dca1f",
    	"Microsoft Edge" : "e9c51622-460d-4d3d-952d-966a5b1da34c",
    	"Microsoft Edge2" : "ecd6b820-32c2-49b6-98a6-444530e5a77a",
    	"Microsoft Edge3" : "f44b1140-bc5e-48c6-8dc0-5cf5a53c0e34",
    	"Microsoft Exchange REST API Based Powershell" : "fb78d390-0c51-40cd-8e17-fdbfab77341b",
    	"Microsoft Flow Mobile PROD-GCCH-CN" : "57fcbcfa-7cee-4eb1-8b25-12d2030b4ee0",
    	"Microsoft Flow" : "57fcbcfa-7cee-4eb1-8b25-12d2030b4ee0",
    	"Microsoft Intune Company Portal" : "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223",
    	"Microsoft Intune Windows Agent" : "fc0f3af4-6835-4174-b806-f7db311fd2f3",
    	"Microsoft Lists App on Android" : "a670efe7-64b6-454f-9ae9-4f1cf27aba58",
    	"Microsoft Office" : "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    	"Microsoft Planner" : "66375f6b-983f-4c2c-9701-d680650f588f",
    	"Microsoft Power BI" : "c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12",
    	"Microsoft Stream Mobile Native" : "844cca35-0656-46ce-b636-13f48b0eecbd",
    	"Microsoft Teams - Device Admin Agent" : "87749df4-7ccf-48f8-aa87-704bad0e0e16",
    	"Microsoft Teams-T4L" : "8ec6bc83-69c8-4392-8f08-b3c986009232",
    	"Microsoft Teams" : "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
    	"Microsoft To-Do client" : "22098786-6e16-43cc-a27d-191a01a1e3b5",
    	"Microsoft Tunnel" : "eb539595-3fe1-474e-9c1d-feb3625d1be5",
    	"Microsoft Whiteboard Client" : "57336123-6e14-4acc-8dcf-287b6088aa28",
    	"ODSP Mobile Lists App" : "540d4ff4-b4c0-44c1-bd06-cab1782d582a",
    	"Office 365 Exchange Online" : "00000002-0000-0ff1-ce00-000000000000",
    	"Office 365 Management" : "00b41c95-dab0-4487-9791-b9d2c32c80f2",
    	"Office UWP PWA" : "0ec893e0-5785-4de6-99da-4ed124e5296c",
    	"OneDrive iOS App" : "af124e86-4e96-495a-b70a-90f90ab96707",
    	"OneDrive SyncEngine" : "ab9b8c07-8f02-4f72-87fa-80105867a763",
    	"OneDrive" : "b26aadf8-566f-4478-926f-589f601d9c74",
    	"Outlook Lite" : "e9b154d0-7658-433b-bb25-6b8e0a8a7c59",
    	"Outlook Mobile" : "27922004-5251-4030-b22d-91ecd9a37ea4",
    	"PowerApps" : "4e291c71-d680-4d0e-9640-0a3358e31177",
    	"SharePoint Android" : "f05ff7c9-f75a-4acd-a3b5-f4b6a870245d",
    	"SharePoint" : "d326c1ce-6cc6-4de2-bebc-4591e5e13ef0",
    	"Universal Store Native Client" : "268761a2-03f3-40df-8a8b-c3db24145b6b",
    	"Visual Studio" : "872cd9fa-d31f-45e0-9eab-6e460a02d1f1",
    	"Windows Search" : "26a7ee05-5602-4d76-a7ba-eae8b7b67941",
    	"Windows Spotlight" : "1b3c667f-cde3-4090-b60b-3d2abd0117f0",
    	"Yammer iPhone" : "a569458c-7f2b-45cb-bab9-b7dee514d112",
    	"ZTNA Network Access Client Private" : "760282b4-0cfc-4952-b467-c8e0298fee16",
    	"ZTNA Network Access Client" : "038ddad9-5bbe-4f64-b0cd-12434d1e633b",	
}


# https://www.whatismybrowser.com/guides/the-latest-user-agent/
user_agents = {
  "Android Chrome": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36",
  "iPhone Safari": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
  "Mac Firefox": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:123.0) Gecko/20100101 Firefox/123.0",
  "Chrome OS": "Mozilla/5.0 (X11; CrOS x86_64 15633.69.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.212 Safari/537.36",
  "Linux Firefox": "Mozilla/5.0 (X11; Linux i686; rv:94.0) Gecko/20100101 Firefox/94.0",
  "Windows 10 Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
  "Windows 7 IE11": "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
  "Windows 10 IE11": "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
  "Windows 10 Edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.128",
  "Windows Phone" : "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; NOKIA; Lumia 800)"
}

# taken from TokenTacticsv2
scopes = {
    "Azure Core Management": ("https://management.core.chinacloudapi.cn//.default offline_access openid", "Microsoft Office"),
    "Azure Graph": ("https://graph.chinacloudapi.cn/.default offline_access openid", "Microsoft Office"),
    "Azure KeyVault": ("https://vault.azure.cn/.default offline_access openid", "Microsoft Office"),
    "Azure Management": ("https://management.chinacloudapi.cn//.default offline_access openid", "Microsoft Office"),
    "Azure Storage": ("https://storage.azure.com/.default offline_access openid", "Microsoft Office"),
    "Microsoft Graph": ("https://microsoftgraph.chinacloudapi.cn/.default offline_access openid", "Microsoft Office"),
    "Microsoft Manage": ("https://enrollment.manage.microsoft.com/.default offline_access openid", "Microsoft Office"),
    "Office Apps": ("https://officeapps.live.com/.default offline_access openid", "OneDrive SyncEngine"),
    "Office Manage": ("https://manage.office.com/.default offline_access openid", "Office 365 Management"),
    "OneDrive": ("https://officeapps.live.com/.default offline_access openid", "OneDrive SyncEngine"),
    "Outlook": ("https://outlook.office365.com/.default offline_access openid", "Microsoft Office"),
    "Substrate": ("https://substrate.office.com/.default offline_access openid", "Microsoft Office"),
    "Teams": ("https://api.spaces.skype.com/.default offline_access openid", "Microsoft Teams"),
    "Yammer": ("https://api.spaces.skype.com/.default offline_access openid", "Microsoft Office"),
}

# pretty print dictionaries
def print_aligned(dictionary):
    max_key_length = max(len(key) for key in dictionary.keys())
    for key, value in dictionary.items():
      print(f"{key.ljust(max_key_length)} : {value}")

def get_tenant_id(domain, proxy):
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  url = f"https://login.partner.microsoftonline.cn/{domain}/.well-known/openid-configuration"
  
  response = requests.get(url, proxies=proxy, verify=False)

  if response.status_code == 200:      
      json_text = json.loads(response.text)
      auth_endpoint = json_text.get("authorization_endpoint")
      tenant_id = auth_endpoint.split("/")[3]  
      print(f"[+] Got Tenant ID: {tenant_id}")
      return tenant_id

  else:
     print(f"[!] Error retrieving tenant ID - HTTP Status Code {response.status_code}")
     return

def refresh_authenticate(client_id, user_agent, proxy, tenant_id, refresh_token, scope):
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f"https://login.partner.microsoftonline.cn/{tenant_id}/oauth2/v2.0/token" 

    parameters = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'grant_type': 'refresh_token',
        'scope': scope
    }

    headers = {
        'User-Agent': user_agent[1],
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=parameters, headers=headers, proxies=proxy, verify=False)
    
    if response.status_code == 200:
        success_string = colored("Got Token!","green", attrs=['bold'])
        print(f"[+] {success_string}")
        json_text = json.loads(response.text)
        print(json.dumps(json_text, indent=2))

    else:
        response_data = json.loads(response.text)
        error_description = response_data.get('error_description')
        print(colored(f"[!] Error getting token: {error_description}","red", attrs=['bold']))
       
    return


# main authentication function
def authenticate(username, password, resource, client_id, user_agent, proxy, get_token=False):
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = "https://login.partner.microsoftonline.cn/common/oauth2/token" 

    parameters = {
        'resource': resource[1],
        'client_id': client_id[1],
        'client_info': '1',
        'grant_type': 'password',
        'username': username,
        'password': password,
        'scope': 'openid'
    }

    headers = {
        'User-Agent': user_agent[1],
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=parameters, headers=headers, proxies=proxy, verify=False)
    
    if response.status_code == 200:
        success_string = colored("Success! No MFA","green", attrs=['bold'])
        json_text = json.loads(response.text)
        scope = json_text.get('scope', 'None')
        scope_string = colored(f"Token Scope: {scope}", attrs=['bold'])

        print(f"[+] {resource[0]} - {client_id[0]} - {user_agent[0]} - {success_string} - {scope_string}")

        if get_token:
           print(f"\n{'=' * 35}")
           print("         RAW TOKEN OUTPUT")
           print(f"{'=' * 35}\n")
           print(json.dumps(json_text, indent=2))
           access_token = json_text.get('access_token', 'None')
           refresh_token = json_text.get('refresh_token', 'None')
           id_token = json_text.get('id_token', 'None')
           graphrunner = f"""$tokens = @{{
"access_token" = "{access_token}"
"refresh_token" = "{refresh_token}"
"id_token" = "{id_token}"
}}\n"""
           print(f"\n{'=' * 35}")
           print("     GRAPHRUNNER TOKEN IMPORT")
           print(f"{'=' * 35}\n")
           print(graphrunner)

        else:
          return resource, client_id, user_agent

    else:
        # Standard invalid password
        if "AADSTS50126" in response.text:
            raise ValueError(colored(f"[!] Error validating credentials for {username}","red", attrs=['bold']))
        
        # Invalid Tenant Response
        elif "AADSTS50128" in response.text or "AADSTS50059" in response.text:
            raise ValueError(colored(f"[!] Tenant for account {username} doesn't exist.","red", attrs=['bold']))
        
        # Invalid Username
        elif "AADSTS50034" in response.text:
            raise ValueError(colored(f"[!] The account {username} doesn't exist.","red", attrs=['bold']))
        
        # Microsoft MFA 
        elif "AADSTS50076" in response.text:
            message_string = colored("Microsoft MFA Required or blocked by conditional access","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {user_agent[0]} - {message_string}")
        
        # Must enroll in MFA 
        elif "AADSTS50079" in response.text:
            message_string = colored("MFA enrollment required but not configured!","green", attrs=['bold'])
            print(f"[+] {resource[0]} - {client_id[0]} - {user_agent[0]} - {message_string}")
        
        # Conditional Access 
        elif "AADSTS53003" in response.text:
            message_string = colored("Blocked by conditional access policy","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {user_agent[0]} - {message_string} ")

        # Conditional Access 
        elif "AADSTS50105" in response.text:
            message_string = colored("Application blocked by conditional access policy","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {user_agent[0]} - {message_string} ")
        
        # Third party MFA
        elif "AADSTS50158" in response.text:
            message_string = colored("Third-party MFA required","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {user_agent[0]} - {message_string} ")

        # Compliant Device
        elif "AADSTS53000" in response.text:
            message_string = colored("Requires compliant/managed device","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {user_agent[0]} - {message_string} ")

        # Consent
        elif "AADSTS65001" in response.text:
            message_string = colored("User or administrator has not consented to use the application","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {user_agent[0]} - {message_string} ")
        
        # Disabled application
        elif "AADSTS7000112:" in response.text:
            message_string = colored("Application disabled","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {message_string} ")

        # Locked out account or hitting smart lockout
        elif "AADSTS50053" in response.text:
            raise ValueError(colored(f"[!] The account {username} appears to be locked.","red", attrs=['bold']))
        
        # Disabled account
        elif "AADSTS50057" in response.text:
            raise ValueError(colored(f"[!] The account {username} appears to be disabled.","red", attrs=['bold']))
        
        # Clientid isn't valid for resource
        elif "AADSTS65002" in response.text:
            message_string = colored("Client_id not authorized for resource","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {message_string} ")

        # Assertion or secret required for resource
        elif "AADSTS7000218" in response.text:
            message_string = colored("client_assertion or client_secret required","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {message_string} ")

        # User blocked
        elif "AADSTS53011" in response.text:
            message_string = colored("User blocked due to risk on home tenant","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {message_string} ")
        
        # Suspicious activity
        elif "AADSTS53004" in response.text:
            message_string = colored("Suspicious activity","yellow", attrs=['bold'])
            print(f"[-] {resource[0]} - {client_id[0]} - {message_string} ")

        # Empty password
        elif "AADSTS900144" in response.text:
           raise ValueError(colored(f"[!] No password provided for {username}","red", attrs=['bold']))
        
        # User password is expired
        elif "AADSTS50055" in response.text:
            raise ValueError(colored(f"[!] Password for {username} expired!","red", attrs=['bold']))
        
        # Invalid resource resource
        elif "AADSTS500011" in response.text:
            raise ValueError(colored(f"[!] resource resource {resource[1]} is invalid","red", attrs=['bold']))
        
        # Invalid clientid
        elif "AADSTS700016" in response.text:
            #raise ValueError(colored(f"[!] Clientid {client_id[1]} is invalid","red", attrs=['bold']))
            print(f"[!] Clientid {client_id[1]} is invalid")

        # default unknown
        else:
            response_data = json.loads(response.text)
            error_description = response_data.get('error_description')
            raise ValueError(colored(f"[!] Unknown error encountered: {error_description}","red", attrs=['bold']))

        return
   

# do a test authentication to validate creds and to prevent a bunch of attempts on accounts that throw errors
def do_test_auth(username, password, proxy):
    print("[*] Performing test authentication")
    ua_key = "Windows 10 Chrome"
    ua_value = user_agents[ua_key]
    user_agent = (ua_key, ua_value)
    resource_key = "Azure Graph API"
    resource_value = resources[resource_key]
    resource = (resource_key, resource_value)
    client_key = "Outlook Mobile"
    client_value = client_ids[client_key]
    client_id = (client_key, client_value)
    authenticate(username, password, resource, client_id, user_agent, proxy)

# function to get tokens with a password
def get_token_with_password(username, password, custom_resource, custom_client_id, custom_user_agent, proxy):
    print("[*] Getting token")
    if custom_user_agent is None:
      print("[-] No User Agent specified, using Windows 10 Chrome")
      ua_key = "Windows 10 Chrome"
      ua_value = user_agents[ua_key]
      user_agent = (ua_key, ua_value)
    else:
      user_agent = ("Custom", custom_user_agent)

    if custom_resource is None:
       print("[-] No resource resource specified. Using Microsoft Graph API")
       custom_resource = "Microsoft Graph API"

    # check if resource provided is a key in resources dict
    if custom_resource in resources:
      resource_value = resources[custom_resource]
      resource = (custom_resource, resource_value)

    # check if resource provided is a value in resources dict
    elif custom_resource in resources.values():
       for key, value in resources.items(): 
          if value == custom_resource:
             resource = (key, custom_resource)
    
    # otherwise just add the Custom tag
    else:
       resource = ("Custom", custom_resource)

    if custom_client_id is None:
       print("[-] No client id specified. Using Microsoft Office")
       custom_client_id = "Microsoft Office"

    if custom_client_id in client_ids:
      client_id_value = client_ids[custom_client_id]
      client_id = (custom_client_id, client_id_value)
    
    else:
       client_id = ("Custom", custom_client_id)

    try:
      authenticate(username, password, resource, client_id, user_agent, proxy, True)
    except ValueError as e:
       print(e)

# function to get tokens with a refresh token
def get_token_with_refresh(tenant_id, client_id, user_agent, proxy, scope, refresh_token):
    
    if scope is None:
       print("[-] No token scope specified. Use '-s' argument")
       sys.exit()

   # check if scope provided is a key in scopes dict
    if scope in scopes:
      scope_value, client_id_ref = scopes[scope]

      if client_id is None:
        client_id = client_ids[client_id_ref]
    else:
       print("[-] Unknown token scope specified. List with --list_scopes")
       sys.exit()

    
    if user_agent is None:
      print("[-] No User Agent specified, using Windows 10 Chrome")
      ua_key = "Windows 10 Chrome"
      ua_value = user_agents[ua_key]
      user_agent = (ua_key, ua_value)
    else:
      user_agent = ("Custom", user_agent)

    try:
       print(f"[*] Getting token for {scope} with client_id: {client_id}")
       refresh_authenticate(client_id, user_agent, proxy, tenant_id, refresh_token, scope_value)
    except ValueError as e:
       print(e)

def get_azure_token_via_adfs(username, password, scope, custom_user_agent, client_id, adfs_url ,proxies, ua_name=None):

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if scope is None:
       print("[-] No token scope specified. Use '-s' argument")
       sys.exit()

   # check if scope provided is a key in scopes dict
    if scope in scopes:
      scope_value, client_id_ref = scopes[scope]

      if client_id is None:
        client_id = client_ids[client_id_ref]
    else:
       print("[-] Unknown token scope specified. List with --list_scopes")
       sys.exit()

    if custom_user_agent is None:
      ua_key = "Windows 10 Chrome"
      ua_value = user_agents[ua_key]
      user_agent = (ua_key, ua_value)
    else:
      if ua_name is not None:
         user_agent = (ua_name, custom_user_agent)
      else:
        user_agent = ("Custom", custom_user_agent)

    azure_token_endpoint="https://login.microsoftonline.com/organizations/oauth2/v2.0/token"

    ws_trust_url = f"{adfs_url}/adfs/services/trust/13/usernamemixed"
    now = datetime.utcnow()
    created = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    expires = (now + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    message_id = f"urn:uuid:{str(uuid.uuid4())}"

    soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
                xmlns:wsa="http://www.w3.org/2005/08/addressing"
                xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
      <s:Header>
        <wsa:Action s:mustUnderstand="1">http://docs.oasis-open.org/ws-sx/ws-trust/200512/RST/Issue</wsa:Action>
        <wsa:MessageID>{message_id}</wsa:MessageID>
        <wsa:ReplyTo>
          <wsa:Address>http://www.w3.org/2005/08/addressing/anonymous</wsa:Address>
        </wsa:ReplyTo>
        <wsa:To s:mustUnderstand="1">{ws_trust_url}</wsa:To>
        <wsse:Security s:mustUnderstand="1"
            xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
          <wsu:Timestamp wsu:Id="_0">
            <wsu:Created>{created}</wsu:Created>
            <wsu:Expires>{expires}</wsu:Expires>
          </wsu:Timestamp>
          <wsse:UsernameToken wsu:Id="ADALUsernameToken">
            <wsse:Username>{username}</wsse:Username>
            <wsse:Password>{password}</wsse:Password>
          </wsse:UsernameToken>
        </wsse:Security>
      </s:Header>
      <s:Body>
        <wst:RequestSecurityToken xmlns:wst="http://docs.oasis-open.org/ws-sx/ws-trust/200512">
          <wsp:AppliesTo xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy">
            <wsa:EndpointReference>
              <wsa:Address>urn:federation:MicrosoftOnline</wsa:Address>
            </wsa:EndpointReference>
          </wsp:AppliesTo>
          <wst:KeyType>http://docs.oasis-open.org/ws-sx/ws-trust/200512/Bearer</wst:KeyType>
          <wst:RequestType>http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue</wst:RequestType>
        </wst:RequestSecurityToken>
      </s:Body>
    </s:Envelope>"""

    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    print("[*] Requesting SAML token from ADFS...")
    response = requests.post(ws_trust_url, data=soap_request.encode('utf-8'),
                             headers=headers, proxies=proxies, verify=False)

    xml = etree.fromstring(response.content)
    saml = xml.find(".//{urn:oasis:names:tc:SAML:1.0:assertion}Assertion")
    if saml is None:
        print("[!] SAML assertion not found - credentials may be invalid")
        print(response.text)
        sys.exit()
        return None

    saml_token = etree.tostring(saml, encoding='unicode')
    saml_b64 = base64.b64encode(saml_token.encode("utf-8")).decode("utf-8")

    print("[+] Got SAML token!")

    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:saml1_1-bearer',
        'client_id': client_id,
        'assertion': saml_b64,
        'scope': scope_value,
    }
    headers = {
       'User-Agent': user_agent[1],
       'Accept': 'application/json',
       'Content-Type': 'application/x-www-form-urlencoded'
    }

    token_response = requests.post(azure_token_endpoint, data=data, proxies=proxies, verify=False, headers=headers)

    if token_response.status_code == 200:
        success_string = colored("Got Token!","green", attrs=['bold'])
        print(f"[+] {scope} - {client_id_ref} - {user_agent[0]} - {success_string}")
        json_text = json.loads(token_response.text)
        print(json.dumps(json_text, indent=2))

    else:
        # Microsoft MFA 
        if "AADSTS50076" in token_response.text:
            message_string = colored("Microsoft MFA Required or blocked by conditional access","yellow", attrs=['bold'])
            print(f"[-] {scope} - {client_id_ref} - {user_agent[0]} - {message_string}")
        
        # Must enroll in MFA 
        elif "AADSTS50079" in token_response.text:
            message_string = colored("MFA enrollment required but not configured!","green", attrs=['bold'])
            print(f"[-] {scope} - {client_id_ref} - {user_agent[0]} - {message_string}")
        
        # Conditional Access 
        elif "AADSTS53003" in token_response.text:
            message_string = colored("Blocked by conditional access policy","yellow", attrs=['bold'])
            print(f"[-] {scope} - {client_id_ref} - {user_agent[0]} - {message_string}")

        # Conditional Access 
        elif "AADSTS50105" in token_response.text:
            message_string = colored("Application blocked by conditional access policy","yellow", attrs=['bold'])
            print(f"[-] {scope} - {client_id_ref} - {user_agent[0]} - {message_string}")
        
        # Third party MFA
        elif "AADSTS50158" in token_response.text:
            message_string = colored("Third-party MFA required","yellow", attrs=['bold'])
            print(f"[-] {scope} - {client_id_ref} - {user_agent[0]} - {message_string}")

        # Compliant Device
        elif "AADSTS53000" in token_response.text:
            message_string = colored("Requires compliant/managed device","yellow", attrs=['bold'])
            print(f"[-] {scope} - {client_id_ref} - {user_agent[0]} - {message_string}")

        # User blocked
        elif "AADSTS53011" in token_response.text:
            message_string = colored("User blocked due to risk on home tenant","yellow", attrs=['bold'])
            print(f"[-] {scope} - {client_id_ref} - {user_agent[0]} - {message_string}")
        
        # Suspicious activity
        elif "AADSTS53004" in token_response.text:
            message_string = colored("Suspicious activity","yellow", attrs=['bold'])
            print(f"[-] {scope} - {client_id_ref} - {user_agent[0]} - {message_string}")
        
        else:
            response_data = json.loads(token_response.text)
            error_description = response_data.get('error_description')
            print(colored(f"[!]{scope} - {client_id_ref} - {user_agent[0]} - {message_string} - Unknown error encountered: {error_description}","red", attrs=['bold']))
        
        return

# handle each combination of parameters
def handle_combination(combination):
    username, password, resource, client_id, user_agent, proxy = combination
    return authenticate(username, password, resource, client_id, user_agent, proxy)
    
# mass check resources, client ids, and user agents
def check_resources(username, password, all_user_agents, threads, custom_user_agent, custom_resource, proxy, custom_client=None):
  print("[*] Starting checks")
  results = []
  resources_to_check = {}
  if custom_resource is not None:
    
    # check if resource provided is a key in resources dict
    if custom_resource in resources:
        resource_value = resources[custom_resource]
        resources_to_check[custom_resource] = resource_value

    # check if resource provided is a value in resources dict
    elif custom_resource in resources.values():
       for key, value in resources.items(): 
          if value == custom_resource:
             resources_to_check[key] = custom_resource
    
    # otherwise just add the Custom tag         
    else:
        resources_to_check["Custom"] = custom_resource
  else:
     resources_to_check = resources

  # Filter client_ids based on custom_client (-c flag)
  if custom_client is not None:
      if custom_client in client_ids:
          client_ids_to_use = {custom_client: client_ids[custom_client]}
      else:
          client_ids_to_use = {"Custom": custom_client}
  else:
      client_ids_to_use = client_ids

  # generate final results dict
  for resource in resources_to_check:
     final_results[resource] = {'Accessible': False, 'Accessible Client IDs': 0}
  
  if all_user_agents:
      combinations = [(username, password, resource, client_id, user_agent, proxy)
                      for resource in resources_to_check.items()
                      for client_id in client_ids_to_use.items()
                      for user_agent in user_agents.items()]
  else:
      if custom_user_agent is not None:
          ua_value = custom_user_agent
          ua_key = "Custom"
          user_agent = (ua_key, ua_value)
      else:
          ua_key = "Windows 10 Chrome"
          ua_value = user_agents[ua_key]
          user_agent = (ua_key, ua_value)
      combinations = [(username, password, resource, client_id, user_agent, proxy)
                      for resource in resources_to_check.items()
                      for client_id in client_ids_to_use.items()]

  try:
    error_raised = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
      try:
        for result in executor.map(handle_combination, combinations):
          results.append(result)
      except ValueError as e:
        # just want to print one time
        if not error_raised:
          error_raised = True
          print(e) 
        sys.exit()

    return results
  
  except KeyboardInterrupt:
    print(colored("[!] Ctrl+C detected, exiting...", "yellow"))
    sys.exit()

# self-explanatory
def write_results(username, results):
  #filter out None results
  filtered_results = [x for x in results if x is not None]
  filename = username + "-accessible.txt"
  with open(filename, "a+") as f:
    for result in filtered_results:
      f.write(', '.join(map(str, result)) + '\n')

  print(f"\n[+] Results written to {filename}\n")

# print out final table
def print_table(results):
  #filter out None results
  filtered_results = [x for x in results if x is not None]

  for result in filtered_results:
    resource_name = result[0][0]
    if resource_name in final_results:
      final_results[resource_name]['Accessible'] = True
      final_results[resource_name]['Accessible Client IDs'] += 1
        
  table_data = []
  for resource, e in final_results.items():
    accessible = e['Accessible']
    if accessible:
        accessible = colored(accessible, 'green',attrs=['bold'])
    else:
       accessible = colored(accessible, 'red',attrs=['bold'])
    table_data.append([resource, accessible, e['Accessible Client IDs']])

  print("\n\n"+tabulate(table_data, headers=[colored("Resource", attrs=['bold']), colored("Accessible w/o MFA",attrs=['bold']), colored("Accessible Client IDs",attrs=['bold'])], tablefmt="grid"))

def add_shared_arguments(parser):
    parser.add_argument('--proxy', metavar="proxy", help="HTTP proxy to use - ie http://127.0.0.1:8080", type=str)
    parser.add_argument('--user_agent', help="User Agent to use", type=str)
    parser.add_argument('-c', metavar="clientid", help="clientid to use", type=str)
    parser.add_argument('-r', metavar="resource", help="resource to use", type=str)
    parser.add_argument('--threads', help="Number of threads to run (Default: 10 threads)", type=int,default=10)
    parser.add_argument('-u', metavar="user", help="User to check", type=str)
    parser.add_argument('-p', metavar="password", help="Password for account", type=str) 

def main():
    banner = "\nFindMeAccess v3.1\n"
    print(banner)

    parser = argparse.ArgumentParser(description='')
    subparsers = parser.add_subparsers(dest='command')

    audit_parser = subparsers.add_parser("audit", help="Used for auditing gaps in MFA")
    add_shared_arguments(audit_parser)
    audit_parser.add_argument('--list_resources', help="List all resources", action='store_true')  
    audit_parser.add_argument('--list_clients', help="List all client ids", action='store_true')  
    audit_parser.add_argument('--list_ua', help="List all user agents", action='store_true')
    audit_parser.add_argument('--ua_all', help="Check all users agents (Default: False)", action='store_true', default=False) 

    token_parser = subparsers.add_parser("token", help="Used for getting tokens")
    add_shared_arguments(token_parser)
    token_parser.add_argument('--list_scopes', help="List all token scopes", action='store_true')
    token_parser.add_argument('-d', help="tenant domain", type=str)
    token_parser.add_argument('-s',  help="Token scope - show with --list_scopes", type=str)
    token_parser.add_argument('--refresh_token', help="Refresh token", type=str)
    token_parser.add_argument('--get_all', help="Get tokens for every scope", action='store_true')

    adfs_parser = subparsers.add_parser("adfs", help="Used for auditing gaps in federated setups with ADFS")
    add_shared_arguments(adfs_parser)
    adfs_parser.add_argument('--list_scopes', help="List all token scopes", action='store_true')
    adfs_parser.add_argument('-s',  help="Token scope - show with --list_scopes", type=str)
    adfs_parser.add_argument('--get_all', help="Get tokens for every scope", action='store_true')
    adfs_parser.add_argument('--url',  help="ADFS endpoint ex - https://adfs.domain.com", type=str)
    adfs_parser.add_argument('--ua_all', help="Check all users agents (Default: False)", action='store_true', default=False)
  
        

    args = parser.parse_args()
    if len(sys.argv) == 1:
      parser.print_help()
      sys.exit()

    if args.proxy:
      proxies = {
            "http": args.proxy, 
            "https": args.proxy
            }
    else:
      proxies = {}
    
    if args.command == "audit":
      if args.list_resources:
        print_aligned(resources)
      
      elif args.list_clients:
        print_aligned(client_ids)

      elif args.list_ua:
        print_aligned(user_agents)

      else:
        
        if not args.u:
          print("[-] No username specified with '-u' option")
          sys.exit()
        
        if not args.p:
          password = getpass.getpass()
        else:
          password = args.p
        

        try:
          do_test_auth(args.u, password, proxies)
          print("[+] Test authentication successful!")

        except Exception as e:
          print(e)
          print("[!] Exception caught, exiting...")
          sys.exit()

        try:
          results = check_resources(args.u, password, args.ua_all, args.threads, args.user_agent, args.r, proxies, args.c)
          if not args.ua_all:
            print_table(results)
          write_results(args.u, results)

        except Exception as e:
            print(e)
            print("[!] Exception caught, exiting...")
            sys.exit()
    
    elif args.command == "token":

      if args.list_scopes:
        print_aligned(scopes)
      
      else:
          if args.u:
            if not args.p:
              password = getpass.getpass()
            else:
                password = args.p

            get_token_with_password(args.u, password, args.r, args.c, args.user_agent, proxies)

          else:
            if not args.d:
              print("[-] No domain specified with '-d' option")
              sys.exit()

            tenant_id = get_tenant_id(args.d, proxies)

            if tenant_id is not None :
                
                if args.refresh_token is not None:
                  if args.get_all:
                    for scope in scopes:
                        get_token_with_refresh(tenant_id, args.c, args.user_agent, proxies, scope, args.refresh_token)
                  else:
                    get_token_with_refresh(tenant_id, args.c, args.user_agent, proxies, args.s, args.refresh_token)
                
                else:
                   print("[-] No refresh token specified with '--refresh_token' option")

            else:
              print("[-] Exiting due to tenant ID failure - check domain name")
    
    elif args.command == "adfs":

      if args.list_scopes:
        print_aligned(scopes)
        return

      if not args.url:
         print("[!] ADFS URL required via --url")
         return
      
      else:
          if args.u:
            if not args.p:
              password = getpass.getpass()
            else:
                password = args.p
            
            if args.get_all:
              for scope in scopes:
                if not args.ua_all:
                  get_azure_token_via_adfs(args.u, password, scope, args.user_agent, args.c, args.url, proxies)
                else:
                   for ua_name, user_agent in user_agents.items():
                      get_azure_token_via_adfs(args.u, password, scope, user_agent, args.c, args.url, proxies, ua_name)
                      
            else:
              if not args.ua_all:
                get_azure_token_via_adfs(args.u, password, args.s, args.user_agent, args.c, args.url, proxies)
              else:
                 for ua_name, user_agent in user_agents.items():
                      get_azure_token_via_adfs(args.u, password, args.s, user_agent, args.c, args.url, proxies, ua_name)
          
if __name__ == "__main__":
    main()
