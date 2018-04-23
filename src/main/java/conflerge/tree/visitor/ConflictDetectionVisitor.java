package conflerge.tree.visitor;

import java.util.ArrayList;
import java.util.List;

import com.github.javaparser.ast.ArrayCreationLevel;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.PackageDeclaration;
import com.github.javaparser.ast.body.AnnotationDeclaration;
import com.github.javaparser.ast.body.AnnotationMemberDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.EmptyMemberDeclaration;
import com.github.javaparser.ast.body.EnumConstantDeclaration;
import com.github.javaparser.ast.body.EnumDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.InitializerDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.comments.BlockComment;
import com.github.javaparser.ast.comments.JavadocComment;
import com.github.javaparser.ast.comments.LineComment;
import com.github.javaparser.ast.expr.ArrayAccessExpr;
import com.github.javaparser.ast.expr.ArrayCreationExpr;
import com.github.javaparser.ast.expr.ArrayInitializerExpr;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.BooleanLiteralExpr;
import com.github.javaparser.ast.expr.CastExpr;
import com.github.javaparser.ast.expr.CharLiteralExpr;
import com.github.javaparser.ast.expr.ClassExpr;
import com.github.javaparser.ast.expr.ConditionalExpr;
import com.github.javaparser.ast.expr.DoubleLiteralExpr;
import com.github.javaparser.ast.expr.EnclosedExpr;
import com.github.javaparser.ast.expr.FieldAccessExpr;
import com.github.javaparser.ast.expr.InstanceOfExpr;
import com.github.javaparser.ast.expr.IntegerLiteralExpr;
import com.github.javaparser.ast.expr.LambdaExpr;
import com.github.javaparser.ast.expr.LongLiteralExpr;
import com.github.javaparser.ast.expr.MarkerAnnotationExpr;
import com.github.javaparser.ast.expr.MemberValuePair;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.MethodReferenceExpr;
import com.github.javaparser.ast.expr.Name;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.NormalAnnotationExpr;
import com.github.javaparser.ast.expr.NullLiteralExpr;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.expr.SimpleName;
import com.github.javaparser.ast.expr.SingleMemberAnnotationExpr;
import com.github.javaparser.ast.expr.StringLiteralExpr;
import com.github.javaparser.ast.expr.SuperExpr;
import com.github.javaparser.ast.expr.ThisExpr;
import com.github.javaparser.ast.expr.TypeExpr;
import com.github.javaparser.ast.expr.UnaryExpr;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.stmt.AssertStmt;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.BreakStmt;
import com.github.javaparser.ast.stmt.CatchClause;
import com.github.javaparser.ast.stmt.ContinueStmt;
import com.github.javaparser.ast.stmt.DoStmt;
import com.github.javaparser.ast.stmt.EmptyStmt;
import com.github.javaparser.ast.stmt.ExplicitConstructorInvocationStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.ForStmt;
import com.github.javaparser.ast.stmt.ForeachStmt;
import com.github.javaparser.ast.stmt.IfStmt;
import com.github.javaparser.ast.stmt.LabeledStmt;
import com.github.javaparser.ast.stmt.LocalClassDeclarationStmt;
import com.github.javaparser.ast.stmt.ReturnStmt;
import com.github.javaparser.ast.stmt.SwitchEntryStmt;
import com.github.javaparser.ast.stmt.SwitchStmt;
import com.github.javaparser.ast.stmt.SynchronizedStmt;
import com.github.javaparser.ast.stmt.ThrowStmt;
import com.github.javaparser.ast.stmt.TryStmt;
import com.github.javaparser.ast.stmt.WhileStmt;
import com.github.javaparser.ast.type.ArrayType;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.type.IntersectionType;
import com.github.javaparser.ast.type.PrimitiveType;
import com.github.javaparser.ast.type.TypeParameter;
import com.github.javaparser.ast.type.UnionType;
import com.github.javaparser.ast.type.UnknownType;
import com.github.javaparser.ast.type.VoidType;
import com.github.javaparser.ast.type.WildcardType;
import com.github.javaparser.ast.visitor.Visitable;

import conflerge.ConflergeUtil;
import conflerge.tree.DiffResult;
import conflerge.tree.ast.NodeListWrapper;

/**
 * Traverses a tree with a DiffResult, and reports a conflict if it encounters a 
 * node corresponding to an operation in that DiffResult.  Used to check that a 
 * subtree that has been deleted or replaced by one set of edits doesn't contain 
 * edits from the other set.
 */
@SuppressWarnings("deprecation")
public class ConflictDetectionVisitor extends ModifierVisitor<DiffResult> {

    /**
     * Vist a NodeList. This must be a NodeListWrapper, because the AST in
     * question should always be wrapped. Report a conflict if there are any
     * insertions under this NodesListWrapper, then visit the nodes
     * it contains.
     */
    @SuppressWarnings({ "rawtypes", "unchecked" })
    @Override
    public Visitable visit(NodeList n, DiffResult args) {
        if (n instanceof NodeListWrapper) {
            if (args.listInserts.containsKey(n)) {
                ConflergeUtil.reportConflict();
                return n;
            }
            NodeList nl = ((NodeListWrapper) n).nodeList; 
            List<Node> nodes = new ArrayList<>(nl);
            for (Node node : nodes) {
                node.accept(this, args);
            }  
            return nl;
        } else {
            System.err.println("Unexpected unwrapped NodeList " + n.size());
            if (n.size() > 0) System.err.println(n.get(0).getClass()); 
            System.err.println(n.getParentNode().get() + " " + n.getParentNode().get().getClass());
            return super.visit(n, args);
        }
    }
    
    // It would be nice to refactor the methods below, but we can't: they
    // need to call the superclass methods, which won't work if the Node
    // type is genericized.
    
    @Override
    public Visitable visit(final AnnotationDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final AnnotationMemberDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ArrayAccessExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ArrayCreationExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ArrayInitializerExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final AssertStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final AssignExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final BinaryExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final BlockStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final BooleanLiteralExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final BreakStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final CastExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final CatchClause n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final CharLiteralExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ClassExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ClassOrInterfaceDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ClassOrInterfaceType n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final CompilationUnit n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ConditionalExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ConstructorDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ContinueStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final DoStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final DoubleLiteralExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final EmptyMemberDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final EmptyStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final EnclosedExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final EnumConstantDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final EnumDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ExplicitConstructorInvocationStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ExpressionStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final FieldAccessExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final FieldDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ForeachStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ForStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final IfStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final InitializerDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final InstanceOfExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final IntegerLiteralExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final JavadocComment n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final LabeledStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final LongLiteralExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final MarkerAnnotationExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final MemberValuePair n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final MethodCallExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final MethodDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final NameExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final NormalAnnotationExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final NullLiteralExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ObjectCreationExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final PackageDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final Parameter n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final Name n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final PrimitiveType n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(SimpleName n, DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(ArrayType n, DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(ArrayCreationLevel n, DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final IntersectionType n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final UnionType n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ReturnStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final SingleMemberAnnotationExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final StringLiteralExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final SuperExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final SwitchEntryStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final SwitchStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final SynchronizedStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ThisExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final ThrowStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final TryStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final LocalClassDeclarationStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final TypeParameter n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final UnaryExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final UnknownType n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final VariableDeclarationExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final VariableDeclarator n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final VoidType n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final WhileStmt n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final WildcardType n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final LambdaExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final MethodReferenceExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final TypeExpr n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Node visit(final ImportDeclaration n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final BlockComment n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(final LineComment n, final DiffResult arg) {
        if (arg.replaced(n) || arg.deleted(n) || arg.modifiers.containsKey(n)) {
            ConflergeUtil.reportConflict();
            return n;
        }
        return super.visit(n, arg);
    }
}
