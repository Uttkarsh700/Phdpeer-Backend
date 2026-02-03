/**
 * Global State Module
 * 
 * Central export point for global state store and utilities.
 */

export { useGlobalStateStore, useBaselineStatus, useTimelineStatus, useDoctorStatus, useAnalyticsStatus, useGlobalStateActions } from './store';
export type { GlobalState, BaselineStatus, TimelineStatus, DoctorStatus, AnalyticsStatus } from '../types';
export { initialGlobalState } from '../types';
