import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// --- Organizations ---
export const getOrganizations = () => client.get("/organizations/").then((r) => r.data);
export const createOrganization = (payload) => client.post("/organizations/", payload).then((r) => r.data);
export const getAssets = (orgId) => client.get(`/organizations/${orgId}/assets`).then((r) => r.data);

// --- Scans ---
export const getScans = (orgId) => client.get("/scans/", { params: { organization_id: orgId } }).then((r) => r.data);
export const createScan = (payload) => client.post("/scans/", payload).then((r) => r.data);
export const getScan = (scanId) => client.get(`/scans/${scanId}`).then((r) => r.data);

// --- Findings ---
export const getFindings = (params) => client.get("/findings/", { params }).then((r) => r.data);
export const resolveFinding = (findingId) => client.patch(`/findings/${findingId}/resolve`).then((r) => r.data);

// --- Risk ---
export const getRiskScore = (orgId) => client.get(`/risk/${orgId}`).then((r) => r.data);

// --- Reports ---
export const getExecutiveSummary = (orgId) => client.get(`/reports/${orgId}/executive-summary`).then((r) => r.data);

export default client;
