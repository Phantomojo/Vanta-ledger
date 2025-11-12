# 🤖 MASTER PROMPT - Vanta Ledger AI Assistant Onboarding

Welcome! You are being onboarded to assist with the **Vanta Ledger** project - a NASA-grade, enterprise-level financial management platform.

## 🎯 Your Mission

You will help develop, maintain, and improve Vanta Ledger by:
1. Understanding the complete codebase architecture
2. Following established patterns and best practices
3. Making informed technical decisions
4. Assisting with development tasks

## 📚 Required Reading Sequence

**Read these files IN ORDER** to gain complete context:

### Phase 1: Understanding (Read First)
1. **01-project-overview.md** - What is Vanta Ledger? Core features and purpose
2. **02-architecture.md** - System design, databases, and technical architecture
3. **03-codebase-structure.md** - File organization and important locations

### Phase 2: Technical Details (Read Second)
4. **04-tech-stack.md** - Technologies, frameworks, and tools used
5. **05-api-endpoints.md** - API structure and available endpoints
6. **06-database-schema.md** - Data models and database design

### Phase 3: Workflows (Read Third)
7. **07-development-workflow.md** - How we develop and collaborate
8. **08-testing-strategy.md** - Testing approach and requirements
9. **09-deployment.md** - Deployment models and operations

### Phase 4: Practical Knowledge (Read Last)
10. **10-common-tasks.md** - Frequent development patterns and tasks

## ⚡ After Reading All Files

Once you've completed reading all 10 files above, you should:

### ✅ Confirm Your Understanding
State what you've learned:
- "I've completed onboarding for Vanta Ledger"
- Summarize the key architectural decisions
- Mention the three deployment models
- Identify the hybrid database strategy

### 🤔 Ask Clarifying Questions
If anything is unclear, ask about:
- Specific technical approaches
- Business logic decisions
- Architecture choices
- Current priorities

### 🎯 Request Direction
Ask the developer:
**"I'm ready to assist with Vanta Ledger. What would you like me to help with?"**

Possible areas of assistance:
- Adding new features
- Fixing bugs
- Improving performance
- Enhancing security
- Writing documentation
- Refactoring code
- Adding tests
- Reviewing PRs

## 🔑 Key Context to Remember

### Project Type
- **Enterprise financial management platform**
- **Multi-tenant SaaS** (10+ companies, 240+ users)
- **Document-centric** with AI-powered processing
- **Production-ready** (version 2.0.0)

### Architecture
- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18 + TypeScript + Vite
- **Databases**: PostgreSQL + MongoDB + Redis (hybrid)
- **AI/ML**: Local LLM integration for document processing

### Three Entry Points
1. `main.py` - Full production (all databases + AI)
2. `simple_main.py` - Simplified (PostgreSQL only)
3. `main_simple.py` - Testing (no databases)

### Critical Patterns
- **Multi-tenancy**: Company-based data isolation
- **Security-first**: JWT auth, rate limiting, password policies
- **Environment-based config**: No hardcoded secrets
- **Modular dependencies**: base/prod/dev/ai requirements

## 🚨 Important Constraints

### Always Remember
- **Backward compatibility**: Existing functionality must work
- **Zero breaking changes**: Unless explicitly requested
- **Security first**: No secrets in code, validate inputs
- **Multi-tenant aware**: All queries must respect company isolation
- **Test your changes**: Write tests for new functionality

### Never Do
- ❌ Commit secrets or credentials
- ❌ Break existing API contracts
- ❌ Remove working features
- ❌ Bypass security measures
- ❌ Mix company data across tenants
- ❌ Hardcode configuration values

## 📖 Documentation References

After onboarding, you can reference these existing docs:
- `README.md` - Project overview and features
- `QUICK_START.md` - Setup and installation guide
- `ENTRY_POINTS_GUIDE.md` - Which main.py to use
- `CODEBASE_REVIEW_RECOMMENDATIONS.md` - Architecture analysis
- `.github/SECURITY.md` - Security policy

## 🎓 Your Onboarding Checklist

- [ ] Read 01-project-overview.md
- [ ] Read 02-architecture.md
- [ ] Read 03-codebase-structure.md
- [ ] Read 04-tech-stack.md
- [ ] Read 05-api-endpoints.md
- [ ] Read 06-database-schema.md
- [ ] Read 07-development-workflow.md
- [ ] Read 08-testing-strategy.md
- [ ] Read 09-deployment.md
- [ ] Read 10-common-tasks.md
- [ ] Confirm understanding to developer
- [ ] Ask for first task assignment

## 🚀 Let's Begin!

**Start by reading** `.ai/01-project-overview.md` and continue through the sequence.

After completing all files, report back and ask: **"What should we work on?"**

---

**Version**: 2.0.0  
**Last Updated**: November 12, 2025  
**Status**: Ready for AI Assistant Onboarding
