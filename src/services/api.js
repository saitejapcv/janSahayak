/**
 * JanSahayak API Client
 * Connects to the AWS API Gateway endpoint to query government schemes.
 * Uses local proxy '/api' in browser environments to avoid browser CORS restrictions,
 * with fallback to the direct AWS API Gateway endpoint.
 */

const DIRECT_API_URL = 'https://ddf6zddofk.execute-api.us-east-1.amazonaws.com';

/**
 * Searches government schemes matching a user's query and optional demographic profile.
 * 
 * @param {string} query - Citizen's freeform need (e.g. "college scholarship")
 * @param {Object} profile - Citizen's optional profile data
 * @returns {Promise<{
 *   query: string,
 *   profile: Object,
 *   bedrock_available: boolean,
 *   answer: string,
 *   matches: Array<Object>
 * }>}
 */
export async function searchSchemes(query, profile = {}) {
  // Clean up profile payload: omit undefined/null/empty strings, format numbers
  const cleanedProfile = {};

  if (profile.age !== undefined && profile.age !== '') {
    const ageNum = Number(profile.age);
    if (!isNaN(ageNum)) cleanedProfile.age = ageNum;
  }

  if (profile.education && profile.education.trim()) {
    cleanedProfile.education = profile.education.trim();
  }

  if (profile.education_level && profile.education_level.trim()) {
    cleanedProfile.education_level = profile.education_level.trim();
  }

  if (profile.course && profile.course.trim()) {
    cleanedProfile.course = profile.course.trim();
  }

  if (profile.family_income !== undefined && profile.family_income !== '') {
    const incomeNum = Number(profile.family_income);
    if (!isNaN(incomeNum)) cleanedProfile.family_income = incomeNum;
  }

  if (profile.state && profile.state.trim()) {
    cleanedProfile.state = profile.state.trim();
  }

  if (profile.category && profile.category.trim()) {
    cleanedProfile.category = profile.category.trim();
  }

  if (typeof profile.disability === 'boolean') {
    cleanedProfile.disability = profile.disability;
  }

  // If in browser, use the Vite '/api' proxy first to prevent browser CORS blockages.
  const isBrowser = typeof window !== 'undefined';
  const customUrl = typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL;
  
  const endpoints = [];
  if (customUrl && customUrl.startsWith('/')) {
    endpoints.push(`${customUrl}/search`);
  } else if (isBrowser) {
    endpoints.push('/api/search');
  }
  endpoints.push(`${DIRECT_API_URL}/search`);

  let lastError = null;

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query ? query.trim() : '',
          profile: cleanedProfile,
        }),
      });

      if (!response.ok) {
        throw new Error(`Service responded with HTTP status ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      lastError = error;
      // If there is another endpoint to try, continue
      if (endpoints.indexOf(endpoint) < endpoints.length - 1) {
        console.warn(`[JanSahayak] Failed calling ${endpoint}, attempting fallback...`, error.message);
      }
    }
  }

  console.error('[JanSahayak API Error]:', lastError);
  throw lastError;
}
