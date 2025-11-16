// Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import axiosInstance from '@renderer/services/axiosConfig'
import { get } from 'lodash'

// You.com API request interface
export interface YouComAgentRunRequest {
  agent_id?: string // Optional agent ID (uses default if not provided)
  input: string // Input text for the agent
  stream?: boolean // Whether to stream the response (default: false)
}

// You.com API response interface
export interface YouComAgentRunResponse {
  success: boolean
  agent_id: string
  result: any // The actual result from You.com API
}

// You.com status interface
export interface YouComStatusResponse {
  enabled: boolean
  api_key_configured: boolean
  default_agent_id: string | null
  base_url: string
  ready: boolean
}

// API response structure
export interface ApiResponse<T> {
  code: number
  status: number
  message: string
  data: T
}

/**
 * Run a You.com agent
 * @param request - Agent run request parameters
 * @returns Agent run response
 */
export const runYouComAgent = async (
  request: YouComAgentRunRequest
): Promise<YouComAgentRunResponse | undefined> => {
  const res = await axiosInstance.post<ApiResponse<YouComAgentRunResponse>>(
    '/api/youcom/agent/run',
    request
  )
  return get(res, 'data.data')
}

/**
 * Get You.com API configuration status
 * @returns Configuration status
 */
export const getYouComStatus = async (): Promise<YouComStatusResponse | undefined> => {
  const res = await axiosInstance.get<ApiResponse<YouComStatusResponse>>('/api/youcom/status')
  return get(res, 'data.data')
}

/**
 * Convenience function to run agent with default settings
 * @param input - Input text for the agent
 * @param agentId - Optional specific agent ID
 * @returns Agent run response
 */
export const runDefaultYouComAgent = async (
  input: string,
  agentId?: string
): Promise<YouComAgentRunResponse | undefined> => {
  return runYouComAgent({
    input,
    agent_id: agentId,
    stream: false
  })
}
