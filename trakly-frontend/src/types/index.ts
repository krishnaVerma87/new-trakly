// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  organization_name: string;
  organization_slug: string;
  organization_description?: string;
  user_email: string;
  user_password: string;
  user_full_name: string;
  user_timezone?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

// User types
export interface UserResponse {
  id: string;
  organization_id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  avatar_url?: string;
  timezone: string;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

export interface UserWithRolesResponse extends UserResponse {
  roles: RoleResponse[];
}

export interface RoleResponse {
  id: string;
  name: string;
  description?: string;
  is_system_role: boolean;
}

export interface RoleCreate {
  name: string;
  description?: string;
}

export interface RoleUpdate {
  name?: string;
  description?: string;
}

export interface UserCreate {
  organization_id: string;
  email: string;
  full_name: string;
  password: string;
  role_ids: string[];
  timezone?: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  password?: string;
  is_active?: boolean;
  role_ids?: string[];
  avatar_url?: string;
  timezone?: string;
}

export interface UserListParams extends PaginationParams {
  active_only?: boolean;
}

export interface BulkUserInvite {
  email: string;
  full_name: string;
  role_id: string;
}

export interface BulkUserInviteRequest {
  users: BulkUserInvite[];
}

export interface BulkUserInviteResult {
  email: string;
  full_name: string;
  success: boolean;
  user_id?: string;
  error?: string;
  temp_password?: string;
}

export interface BulkUserInviteResponse {
  total: number;
  successful: number;
  failed: number;
  results: BulkUserInviteResult[];
}

// Organization types
export interface OrganizationResponse {
  id: string;
  name: string;
  slug: string;
  description?: string;
  settings?: string | object;  // JSON string or parsed object
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OrganizationUpdate {
  name?: string;
  description?: string;
  settings?: string | object;  // JSON string or object for integration settings
  is_active?: boolean;
}

// Issue types
export type IssueType = 'bug' | 'task' | 'sub_task' | 'story' | 'improvement';
export type IssueStatus = 'new' | 'in_progress' | 'review' | 'done' | 'closed' | 'wont_fix';
export type Priority = 'critical' | 'high' | 'medium' | 'low';
export type Severity = 'blocker' | 'critical' | 'major' | 'minor' | 'trivial';
export type Resolution = 'fixed' | 'duplicate' | 'wont_fix' | 'cannot_reproduce';

export interface IssueCreate {
  project_id: string;
  title: string;
  description?: string;
  issue_type: IssueType;
  priority: Priority;
  severity?: Severity;
  component_id?: string;
  assignee_id?: string;
  parent_issue_id?: string;
  sprint_id?: string;
  label_ids?: string[];
  repro_steps?: string;
  environment?: string;
  stack_trace?: string;
  is_regression?: boolean;
  affected_version?: string;
  feature_id?: string;
  feature_link_type?: string;
  story_points?: number;
  time_estimate_minutes?: number;
}

export interface IssueUpdate {
  title?: string;
  description?: string;
  issue_type?: IssueType;
  status?: IssueStatus;
  priority?: Priority;
  severity?: Severity;
  assignee_id?: string | null;
  component_id?: string | null;
  sprint_id?: string | null;
  workflow_column_id?: string | null;
  label_ids?: string[];
  repro_steps?: string;
  environment?: string;
  stack_trace?: string;
  is_regression?: boolean;
  affected_version?: string;
  resolution?: Resolution;
  story_points?: number;
  time_estimate_minutes?: number;
  time_spent_minutes?: number;
}

export interface LabelResponse {
  id: string;
  project_id: string;
  name: string;
  color: string;
  description?: string;
  created_at: string;
}

export interface IssueResponse {
  id: string;
  organization_id: string;
  project_id: string;
  issue_number: number;
  issue_key: string;
  title: string;
  description?: string;
  issue_type: IssueType;
  status: IssueStatus;
  priority: Priority;
  severity?: Severity;
  reporter_id: string;
  assignee_id?: string;
  assignee?: UserResponse; // Full assignee user object
  component_id?: string;
  parent_issue_id?: string;
  feature_id?: string; // Optional link to parent feature
  sprint_id?: string;
  workflow_column_id?: string;
  repro_steps?: string;
  environment?: string;
  stack_trace?: string;
  is_regression: boolean;
  affected_version?: string;
  story_points?: number;
  time_estimate_minutes?: number;
  time_spent_minutes: number;
  resolution?: Resolution;
  resolved_at?: string;
  is_duplicate: boolean;
  duplicate_of_id?: string;
  labels: LabelResponse[];
  checklists?: ChecklistResponse[];
  created_at: string;
  updated_at: string;
}

export interface ChecklistItemResponse {
  id: string;
  checklist_id: string;
  content: string;
  description?: string;
  assignee_id?: string;
  assignee?: UserResponse;
  is_completed: boolean;
  status: 'pending' | 'in_progress' | 'dev_done' | 'qa_checked';
  position: number;
  created_at: string;
  updated_at: string;
}

export interface ChecklistResponse {
  id: string;
  issue_id: string;
  name: string;
  position: number;
  items: ChecklistItemResponse[];
}

export interface ChecklistCreate {
  name: string;
  position?: number;
}

export interface ChecklistUpdate {
  name?: string;
  position?: number;
}

export interface ChecklistItemCreate {
  content: string;
  description?: string;
  assignee_id?: string;
  position?: number;
}

export interface ChecklistItemUpdate {
  content?: string;
  description?: string;
  assignee_id?: string;
  is_completed?: boolean;
  status?: 'pending' | 'in_progress' | 'dev_done' | 'qa_checked';
  position?: number;
}



export interface IssueWithDetailsResponse extends IssueResponse {
  reporter: UserResponse;
  assignee?: UserResponse;
}

export interface SimilarIssueResponse {
  id: string;
  project_id: string;
  issue_key: string;
  title: string;
  description?: string;
  status: IssueStatus;
  issue_type: IssueType;
  similarity_score: number;
  created_at: string;
}

export interface DuplicateCheckRequest {
  project_id: string;
  title: string;
  description?: string;
}

export interface DuplicateCheckResponse {
  similar_issues: SimilarIssueResponse[];
  suggested_deduplication_hash: string;
  is_likely_duplicate: boolean;
}

// Project types
export interface ComponentResponse {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  lead_user_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectMemberResponse {
  id: string;
  project_id: string;
  user_id: string;
  role: string;
  user?: UserResponse;
  created_at: string;
}

export interface ProjectCreate {
  name: string;
  key: string;
  organization_id: string;
  slug?: string;
  description?: string;
  lead_user_id?: string;
  default_assignee_id?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  lead_user_id?: string;
  default_assignee_id?: string;
  is_active?: boolean;
}

export interface ProjectResponse {
  id: string;
  organization_id: string;
  name: string;
  key: string;
  slug: string;
  description?: string;
  lead_user_id?: string;
  default_assignee_id?: string;
  is_active: boolean;
  is_pinned?: boolean;
  workflow_template_id?: string;
  workflow_template?: WorkflowTemplateResponse;
  members: ProjectMemberResponse[];
  components: ComponentResponse[];
  created_at: string;
  updated_at: string;
}

// Reminder types
export interface ReminderRuleConditions {
  days_without_update: number;
  status?: string[];
  priority?: string[];
  sprint?: 'current' | 'next' | 'any';
  assignee_exists?: boolean;
  issue_type?: string[];
}

export interface ReminderRuleResponse {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  is_enabled: boolean;
  conditions: ReminderRuleConditions;
  notification_title: string;
  notification_message: string;
  notify_assignee: boolean;
  notify_watchers: boolean;
  notify_project_managers: boolean;
  check_frequency_minutes: number;
  last_executed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ReminderRuleCreate {
  project_id: string;
  name: string;
  description?: string;
  is_enabled?: boolean;
  conditions: ReminderRuleConditions;
  notification_title: string;
  notification_message: string;
  notify_assignee?: boolean;
  notify_watchers?: boolean;
  notify_project_managers?: boolean;
  check_frequency_minutes?: number;
}

export interface ReminderRuleUpdate {
  name?: string;
  description?: string;
  is_enabled?: boolean;
  conditions?: ReminderRuleConditions;
  notification_title?: string;
  notification_message?: string;
  notify_assignee?: boolean;
  notify_watchers?: boolean;
  notify_project_managers?: boolean;
  check_frequency_minutes?: number;
}


export interface ProjectMemberCreate {
  user_id: string;
  role: string;
}

export interface ComponentCreate {
  name: string;
  description?: string;
  lead_user_id?: string;
}

export interface ComponentUpdate {
  name?: string;
  description?: string;
  lead_user_id?: string;
}

// Feature types
export type FeatureStatus = 'backlog' | 'planning' | 'in_progress' | 'testing' | 'completed' | 'cancelled';

export interface FeatureCreate {
  project_id: string;
  title: string;
  description?: string;
  owner_user_id?: string;
  component_id?: string;
  priority: Priority;
  target_release?: string;
  target_date?: string;
}

export interface FeatureUpdate {
  title?: string;
  description?: string;
  owner_user_id?: string;
  component_id?: string;
  status?: FeatureStatus;
  priority?: Priority;
  target_release?: string;
  target_date?: string;
  actual_completion_date?: string;
  progress_percentage?: number;
}

export interface FeatureResponse {
  id: string;
  organization_id: string;
  project_id: string;
  feature_number: number;
  feature_key: string;
  title: string;
  description?: string;
  owner_user_id?: string;
  component_id?: string;
  status: FeatureStatus;
  priority: Priority;
  target_release?: string;
  target_date?: string;
  actual_completion_date?: string;
  progress_percentage: number;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface LinkedIssueInfo {
  id: string;
  issue_key: string;
  title: string;
  issue_type: string;
  status: string;
  severity?: string;
  link_type: string;
}

export interface FeatureWithIssuesResponse extends FeatureResponse {
  linked_issues: LinkedIssueInfo[];
  bug_count: number;
  open_bug_count: number;
}

// Dashboard types
export interface DashboardStats {
  projects: {
    total: number;
  };
  issues: {
    total: number;
    open: number;
    closed: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
  };
  features: {
    total: number;
  };
  bugs: {
    total: number;
    open: number;
  };
}

export interface BugsPerFeatureResponse {
  feature_id: string;
  feature_key: string;
  title: string;
  status: string;
  bug_count: number;
  open_bug_count: number;
}

export interface RecentIssueResponse {
  id: string;
  issue_key: string;
  title: string;
  issue_type: string;
  status: string;
  priority: string;
  reporter_name: string;
  assignee_name?: string;
  created_at: string;
}

// Developer Dashboard types
export interface DeveloperDashboardData {
  my_issues: {
    total: number;
    by_priority: Record<string, number>;
    by_status: Record<string, number>;
    critical_count: number;
    high_count: number;
  };
  recent_assigned: Array<{
    id: string;
    issue_key: string;
    title: string;
    issue_type: string;
    status: string;
    priority: string;
    project_name: string | null;
    created_at: string;
  }>;
  time_tracking: {
    total_spent_minutes: number;
    total_estimated_minutes: number;
    total_spent_hours: number;
    total_estimated_hours: number;
  };
}

// Project Manager Dashboard types
export interface ProjectManagerDashboardData {
  active_sprints: Array<{
    id: string;
    name: string;
    goal: string | null;
    start_date: string;
    end_date: string;
    total_issues: number;
    completed_issues: number;
    progress_percentage: number;
  }>;
  team_workload: Array<{
    user_id: string;
    user_name: string;
    active_issues: number;
  }>;
  pending_issues: number;
  blocked_issues: number;
  summary: {
    active_sprint_count: number;
    team_members: number;
  };
}

// API Response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Pagination
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

// List filters
export interface IssueFilterParams extends PaginationParams {
  project_id?: string;
  status?: IssueStatus;
  issue_type?: IssueType;
  priority?: Priority;
  assignee_id?: string;
  component_id?: string;
  search?: string;
  sprint_id?: string;
  include_backlog?: boolean;
  exclude_completed_sprints?: boolean;
}

export interface FeatureFilterParams extends PaginationParams {
  project_id: string;
  status?: FeatureStatus;
}

// Sprint types
export type SprintStatus = 'planned' | 'active' | 'completed';

export interface SprintCreate {
  project_id: string;
  name: string;
  goal?: string;
  start_date: string;
  end_date: string;
}

export interface SprintUpdate {
  name?: string;
  goal?: string;
  start_date?: string;
  end_date?: string;
  status?: SprintStatus;
}

export interface SprintResponse {
  id: string;
  project_id: string;
  name: string;
  goal?: string;
  start_date: string;
  end_date: string;
  status: SprintStatus;
  issue_count: number;
  completed_issue_count: number;
  created_at: string;
  updated_at: string;
}

export interface SprintWithIssuesResponse extends SprintResponse {
  issues: IssueResponse[];
}

// Comment types
export interface CommentResponse {
  id: string;
  issue_id?: string;
  feature_id?: string;
  user_id: string;
  content: string;
  is_internal: boolean;
  user: UserResponse;
  created_at: string;
  updated_at: string;
}

// Settings types
export interface SettingsTab {
  id: string;
  label: string;
  icon: string;
  requiresAdmin: boolean;
}

// Activity types
export interface ActivityItem {
  id: string;
  entity_type: string;
  entity_id: string;
  issue_id?: string; // For backwards compatibility
  user_id: string | null;
  user: UserResponse | null;
  action_type: string;
  old_value?: any;
  new_value?: any;
  additional_data?: any;
  // Legacy fields for backwards compatibility
  field_name?: string;
  from_value?: string;
  to_value?: string;
  details?: string;
  created_at: string;
}

export interface SprintStats {
  total_issues: number;
  completed_issues: number;
  incomplete_issues: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_assignee: Record<string, number>;
}

// Time Tracking types
export interface TimeLogResponse {
  id: string;
  issue_id: string;
  user_id: string;
  user_name?: string;
  started_at: string;
  ended_at?: string;
  duration_minutes?: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface TimeLogSummary {
  total_time_minutes: number;
  total_time_hours: number;
  log_count: number;
  by_user: Record<string, number>;
}

// Wiki Page types
export interface WikiPageBase {
  title: string;
  content: string;
  slug?: string;
  parent_id?: string;
}

export interface WikiPageCreate extends WikiPageBase {}

export interface WikiPageUpdate {
  title?: string;
  content?: string;
  slug?: string;
}

export interface WikiPageMove {
  parent_id?: string;
  position: number;
}

export interface UserBrief {
  id: string;
  email: string;
  full_name: string;
}

export interface WikiPageResponse {
  id: string;
  project_id: string;
  parent_id?: string;
  title: string;
  slug: string;
  content: string;
  position: number;
  created_by: string;
  updated_by?: string;
  creator?: UserBrief;
  updater?: UserBrief;
  created_at: string;
  updated_at: string;
}

export interface WikiPageTreeNode {
  id: string;
  title: string;
  slug: string;
  parent_id?: string;
  position: number;
  created_at: string;
  updated_at: string;
  children: WikiPageTreeNode[];
}

// Workflow Template types
export interface WorkflowColumnBase {
  name: string;
  position: number;
  wip_limit?: number;
  color?: string;
}

export interface WorkflowColumnCreate extends WorkflowColumnBase {}

export interface WorkflowColumnUpdate {
  name?: string;
  position?: number;
  wip_limit?: number;
  color?: string;
}

export interface WorkflowColumnResponse extends WorkflowColumnBase {
  id: string;
  template_id: string;
  created_at: string;
  updated_at: string;
  issue_count?: number;
}

export interface WorkflowTemplateBase {
  name: string;
  description?: string;
}

export interface WorkflowTemplateCreate extends WorkflowTemplateBase {
  columns: WorkflowColumnCreate[];
  is_default?: boolean;
}

export interface WorkflowTemplateUpdate {
  name?: string;
  description?: string;
  is_default?: boolean;
}

export interface WorkflowTemplateResponse extends WorkflowTemplateBase {
  id: string;
  organization_id: string;
  is_default: boolean;
  is_system: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  columns: WorkflowColumnResponse[];
  project_count?: number;
}

export interface ColumnChange {
  column_id: string;
  old_name: string;
  new_name: string;
  action: string;
}

export interface ColumnMigrationAction {
  old_column_id: string;
  new_column_id: string;
  issue_ids?: string[];
}

export interface WorkflowColumnBatchUpdate {
  columns: WorkflowColumnCreate[];
  migration_actions?: ColumnMigrationAction[];
}

export interface ColumnMigrationWarning {
  column_id: string;
  column_name: string;
  issue_count: number;
  action: string;
  suggested_target_columns: WorkflowColumnResponse[];
}

export interface WorkflowMigrationPreview {
  template_id: string;
  template_name: string;
  changes: ColumnChange[];
  warnings: ColumnMigrationWarning[];
  safe_to_apply: boolean;
}
